from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import RunStatus, Workflow, WorkflowRun, WorkflowStatus
from app.schemas import DashboardMetrics, RunCreate


def execute_workflow(db: Session, workflow: Workflow, request: RunCreate) -> WorkflowRun:
    if workflow.status != WorkflowStatus.ACTIVE:
        raise ValueError("Only active workflows can be executed.")

    stages = workflow.stages
    automated_stages = sum(1 for stage in stages if bool(stage.get("automated")))
    automation_rate = automated_stages / len(stages)
    duration_seconds = max(0.5, request.input_records * 0.012 * (1.1 - automation_rate))
    saved_minutes = max(0, workflow.manual_minutes - workflow.automated_minutes)
    savings = saved_minutes / 60 * workflow.hourly_cost
    status = RunStatus.FAILED if request.force_failure else RunStatus.SUCCEEDED

    run = WorkflowRun(
        workflow_id=workflow.id,
        status=status,
        triggered_by=request.triggered_by,
        correlation_id=f"run-{uuid4().hex[:12]}",
        input_records=request.input_records,
        output_records=0 if request.force_failure else request.input_records,
        quality_score=0 if request.force_failure else request.quality_score,
        duration_seconds=duration_seconds,
        estimated_savings=0 if request.force_failure else round(savings, 2),
        details={
            "stages_executed": len(stages),
            "automated_stages": automated_stages,
            "automation_rate": round(automation_rate, 4),
            "quality_gate": "failed" if request.force_failure else "passed",
        },
        started_at=datetime.now(UTC).replace(tzinfo=None),
        completed_at=datetime.now(UTC).replace(tzinfo=None),
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def calculate_dashboard_metrics(db: Session) -> DashboardMetrics:
    workflows = list(db.scalars(select(Workflow)).all())
    runs = list(db.scalars(select(WorkflowRun)).all())
    succeeded = [run for run in runs if run.status == RunStatus.SUCCEEDED]
    active = [item for item in workflows if item.status == WorkflowStatus.ACTIVE]

    total_stages = sum(len(workflow.stages) for workflow in active)
    automated_stages = sum(
        sum(1 for stage in workflow.stages if bool(stage.get("automated"))) for workflow in active
    )
    sla_hits = 0
    for run in succeeded:
        workflow = next((item for item in workflows if item.id == run.workflow_id), None)
        if workflow and run.duration_seconds <= workflow.sla_minutes * 60:
            sla_hits += 1

    users = db.scalar(select(func.count(func.distinct(WorkflowRun.triggered_by)))) or 0
    saved_minutes = sum(
        max(0, workflow.manual_minutes - workflow.automated_minutes) for workflow in active
    )
    return DashboardMetrics(
        active_workflows=len(active),
        total_runs=len(runs),
        success_rate=round(len(succeeded) / len(runs) * 100, 1) if runs else 0,
        automation_rate=round(automated_stages / total_stages * 100, 1) if total_stages else 0,
        sla_attainment=round(sla_hits / len(succeeded) * 100, 1) if succeeded else 0,
        average_quality=round(sum(run.quality_score for run in succeeded) / len(succeeded) * 100, 1)
        if succeeded
        else 0,
        records_processed=sum(run.output_records for run in succeeded),
        hours_saved=round(saved_minutes * len(succeeded) / 60, 1),
        estimated_savings=round(sum(run.estimated_savings for run in succeeded), 2),
        adoption_users=int(users),
    )
