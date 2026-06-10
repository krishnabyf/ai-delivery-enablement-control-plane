from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import Base, SessionLocal, engine, get_db
from app.models import Review, Workflow, WorkflowRun
from app.schemas import (
    DashboardMetrics,
    ReviewCreate,
    RunCreate,
    RunRead,
    WorkflowCreate,
    WorkflowRead,
)
from app.security import require_api_key
from app.seed import seed_demo_data
from app.services import calculate_dashboard_metrics, execute_workflow

BASE_DIR = Path(__file__).resolve().parent
settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    if settings.seed_demo_data:
        with SessionLocal() as db:
            seed_demo_data(db)
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Governed workflow automation, delivery health, and operational intelligence.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key"],
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")
DatabaseSession = Annotated[Session, Depends(get_db)]


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def dashboard(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy", "environment": settings.environment, "version": "1.0.0"}


@app.get("/api/v1/metrics", response_model=DashboardMetrics)
def metrics(db: DatabaseSession) -> DashboardMetrics:
    return calculate_dashboard_metrics(db)


@app.get("/api/v1/workflows", response_model=list[WorkflowRead])
def list_workflows(db: DatabaseSession) -> list[Workflow]:
    return list(db.scalars(select(Workflow).order_by(Workflow.name)).all())


@app.post(
    "/api/v1/workflows",
    response_model=WorkflowRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
)
def create_workflow(request: WorkflowCreate, db: DatabaseSession) -> Workflow:
    if db.scalar(select(Workflow).where(Workflow.name == request.name)):
        raise HTTPException(status_code=409, detail="Workflow name already exists.")
    workflow = Workflow(**request.model_dump(mode="json"))
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    return workflow


@app.post(
    "/api/v1/workflows/{workflow_id}/runs",
    response_model=RunRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
)
def run_workflow(workflow_id: int, request: RunCreate, db: DatabaseSession) -> WorkflowRun:
    workflow = db.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found.")
    try:
        return execute_workflow(db, workflow, request)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/api/v1/runs", response_model=list[RunRead])
def list_runs(db: DatabaseSession, limit: int = 20) -> list[WorkflowRun]:
    safe_limit = min(max(limit, 1), 100)
    return list(
        db.scalars(
            select(WorkflowRun).order_by(desc(WorkflowRun.started_at)).limit(safe_limit)
        ).all()
    )


@app.post(
    "/api/v1/runs/{run_id}/reviews",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
)
def create_review(run_id: int, request: ReviewCreate, db: DatabaseSession) -> dict[str, object]:
    if not db.get(WorkflowRun, run_id):
        raise HTTPException(status_code=404, detail="Workflow run not found.")
    review = Review(workflow_run_id=run_id, **request.model_dump())
    db.add(review)
    db.commit()
    db.refresh(review)
    return {"id": review.id, "outcome": review.outcome, "created_at": review.created_at}
