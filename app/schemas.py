from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import RunStatus, WorkflowStatus


class Stage(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    type: str = Field(pattern="^(setup|pre_process|execute|quality_gate|post_process|report)$")
    automated: bool = True


class WorkflowCreate(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=10, max_length=1000)
    owner: str = Field(min_length=2, max_length=120)
    status: WorkflowStatus = WorkflowStatus.ACTIVE
    version: str = "1.0.0"
    stages: list[Stage] = Field(min_length=1)
    manual_minutes: float = Field(ge=0)
    automated_minutes: float = Field(ge=0)
    hourly_cost: float = Field(gt=0)
    sla_minutes: int = Field(gt=0)


class WorkflowRead(WorkflowCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class RunCreate(BaseModel):
    triggered_by: str = Field(min_length=2, max_length=120)
    input_records: int = Field(gt=0, le=1_000_000)
    quality_score: float = Field(default=0.98, ge=0, le=1)
    force_failure: bool = False


class RunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workflow_id: int
    status: RunStatus
    triggered_by: str
    correlation_id: str
    input_records: int
    output_records: int
    quality_score: float
    duration_seconds: float
    estimated_savings: float
    details: dict[str, object]
    started_at: datetime
    completed_at: datetime | None


class ReviewCreate(BaseModel):
    reviewer: str = Field(min_length=2, max_length=120)
    outcome: str = Field(pattern="^(accepted|follow_up|rolled_back)$")
    notes: str = Field(min_length=5, max_length=2000)
    action_owner: str = Field(min_length=2, max_length=120)


class DashboardMetrics(BaseModel):
    active_workflows: int
    total_runs: int
    success_rate: float
    automation_rate: float
    sla_attainment: float
    average_quality: float
    records_processed: int
    hours_saved: float
    estimated_savings: float
    adoption_users: int
