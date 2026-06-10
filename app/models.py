from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class WorkflowStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"


class RunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class Workflow(Base):
    __tablename__ = "workflows"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text)
    owner: Mapped[str] = mapped_column(String(120), index=True)
    status: Mapped[WorkflowStatus] = mapped_column(Enum(WorkflowStatus))
    version: Mapped[str] = mapped_column(String(20), default="1.0.0")
    stages: Mapped[list[dict[str, object]]] = mapped_column(JSON)
    manual_minutes: Mapped[float] = mapped_column(Float, default=0)
    automated_minutes: Mapped[float] = mapped_column(Float, default=0)
    hourly_cost: Mapped[float] = mapped_column(Float, default=45)
    sla_minutes: Mapped[int] = mapped_column(Integer, default=60)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)
    runs: Mapped[list["WorkflowRun"]] = relationship(
        back_populates="workflow", cascade="all, delete-orphan"
    )


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    workflow_id: Mapped[int] = mapped_column(ForeignKey("workflows.id"), index=True)
    status: Mapped[RunStatus] = mapped_column(Enum(RunStatus), index=True)
    triggered_by: Mapped[str] = mapped_column(String(120))
    correlation_id: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    input_records: Mapped[int] = mapped_column(Integer, default=0)
    output_records: Mapped[int] = mapped_column(Integer, default=0)
    quality_score: Mapped[float] = mapped_column(Float, default=0)
    duration_seconds: Mapped[float] = mapped_column(Float, default=0)
    estimated_savings: Mapped[float] = mapped_column(Float, default=0)
    details: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    workflow: Mapped[Workflow] = relationship(back_populates="runs")


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    workflow_run_id: Mapped[int] = mapped_column(ForeignKey("workflow_runs.id"), index=True)
    reviewer: Mapped[str] = mapped_column(String(120))
    outcome: Mapped[str] = mapped_column(String(40))
    notes: Mapped[str] = mapped_column(Text)
    action_owner: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
