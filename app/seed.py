from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Workflow
from app.schemas import RunCreate
from app.services import execute_workflow


def seed_demo_data(db: Session) -> None:
    if db.scalar(select(Workflow.id).limit(1)):
        return

    workflows = [
        Workflow(
            name="Multilingual Data Quality Pipeline",
            description="Validates, normalises, samples, and reports AI training data quality.",
            owner="Data Operations",
            status="active",
            version="2.1.0",
            stages=[
                {"name": "Project setup", "type": "setup", "automated": True},
                {"name": "Schema normalisation", "type": "pre_process", "automated": True},
                {"name": "Policy validation", "type": "quality_gate", "automated": True},
                {"name": "Human exception review", "type": "execute", "automated": False},
                {"name": "Delivery packaging", "type": "post_process", "automated": True},
                {"name": "KPI publication", "type": "report", "automated": True},
            ],
            manual_minutes=210,
            automated_minutes=28,
            hourly_cost=52,
            sla_minutes=45,
        ),
        Workflow(
            name="Contributor Onboarding Automation",
            description="Governed setup and readiness checks for distributed delivery teams.",
            owner="Enablement",
            status="active",
            version="1.4.0",
            stages=[
                {"name": "Request intake", "type": "setup", "automated": True},
                {"name": "Access provisioning", "type": "pre_process", "automated": True},
                {"name": "Compliance check", "type": "quality_gate", "automated": True},
                {"name": "Training confirmation", "type": "execute", "automated": False},
                {"name": "Readiness report", "type": "report", "automated": True},
            ],
            manual_minutes=95,
            automated_minutes=18,
            hourly_cost=45,
            sla_minutes=30,
        ),
        Workflow(
            name="Delivery Closure and Lessons Learned",
            description=(
                "Automates closure evidence, KPI reporting, and post-implementation review."
            ),
            owner="Delivery Excellence",
            status="active",
            version="1.2.0",
            stages=[
                {"name": "Evidence collection", "type": "pre_process", "automated": True},
                {"name": "KPI reconciliation", "type": "quality_gate", "automated": True},
                {"name": "Stakeholder sign-off", "type": "execute", "automated": False},
                {"name": "Case study generation", "type": "post_process", "automated": True},
                {"name": "Portfolio reporting", "type": "report", "automated": True},
            ],
            manual_minutes=150,
            automated_minutes=24,
            hourly_cost=60,
            sla_minutes=60,
        ),
    ]
    db.add_all(workflows)
    db.commit()
    for workflow in workflows:
        db.refresh(workflow)

    demo_runs = [
        (workflows[0], "operations.lead", 12500, 0.992),
        (workflows[0], "quality.manager", 9800, 0.987),
        (workflows[1], "enablement.partner", 420, 0.996),
        (workflows[1], "regional.ops", 310, 0.981),
        (workflows[2], "delivery.director", 34, 0.99),
    ]
    for workflow, user, records, quality in demo_runs:
        execute_workflow(
            db,
            workflow,
            RunCreate(triggered_by=user, input_records=records, quality_score=quality),
        )
