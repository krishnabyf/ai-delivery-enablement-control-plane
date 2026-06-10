from fastapi.testclient import TestClient

WORKFLOW = {
    "name": "Training Data Intake",
    "description": "Standardises delivery setup and input validation.",
    "owner": "Enablement",
    "status": "active",
    "version": "1.0.0",
    "stages": [
        {"name": "Setup", "type": "setup", "automated": True},
        {"name": "Review", "type": "quality_gate", "automated": False},
        {"name": "Report", "type": "report", "automated": True},
    ],
    "manual_minutes": 120,
    "automated_minutes": 20,
    "hourly_cost": 60,
    "sla_minutes": 30,
}


def test_health_and_empty_metrics(client: TestClient) -> None:
    assert client.get("/health").json()["status"] == "healthy"
    metrics = client.get("/api/v1/metrics").json()
    assert metrics["total_runs"] == 0
    assert metrics["success_rate"] == 0


def test_protected_endpoint_requires_key(client: TestClient) -> None:
    response = client.post("/api/v1/workflows", json=WORKFLOW)
    assert response.status_code == 401


def test_workflow_run_and_metrics(client: TestClient, api_headers: dict[str, str]) -> None:
    created = client.post("/api/v1/workflows", json=WORKFLOW, headers=api_headers)
    assert created.status_code == 201
    workflow_id = created.json()["id"]

    run = client.post(
        f"/api/v1/workflows/{workflow_id}/runs",
        json={"triggered_by": "ops.lead", "input_records": 1000, "quality_score": 0.99},
        headers=api_headers,
    )
    assert run.status_code == 201
    assert run.json()["status"] == "succeeded"
    assert run.json()["estimated_savings"] == 100

    metrics = client.get("/api/v1/metrics").json()
    assert metrics["automation_rate"] == 66.7
    assert metrics["success_rate"] == 100
    assert metrics["hours_saved"] == 1.7
    assert metrics["estimated_savings"] == 100


def test_duplicate_workflow_is_rejected(client: TestClient, api_headers: dict[str, str]) -> None:
    assert client.post("/api/v1/workflows", json=WORKFLOW, headers=api_headers).status_code == 201
    assert client.post("/api/v1/workflows", json=WORKFLOW, headers=api_headers).status_code == 409


def test_failed_run_is_visible_in_reliability_metrics(
    client: TestClient, api_headers: dict[str, str]
) -> None:
    workflow = client.post("/api/v1/workflows", json=WORKFLOW, headers=api_headers).json()
    response = client.post(
        f"/api/v1/workflows/{workflow['id']}/runs",
        json={"triggered_by": "qa.lead", "input_records": 20, "force_failure": True},
        headers=api_headers,
    )
    assert response.json()["status"] == "failed"
    assert client.get("/api/v1/metrics").json()["success_rate"] == 0


def test_post_implementation_review(client: TestClient, api_headers: dict[str, str]) -> None:
    workflow = client.post("/api/v1/workflows", json=WORKFLOW, headers=api_headers).json()
    run = client.post(
        f"/api/v1/workflows/{workflow['id']}/runs",
        json={"triggered_by": "delivery.owner", "input_records": 10},
        headers=api_headers,
    ).json()
    response = client.post(
        f"/api/v1/runs/{run['id']}/reviews",
        json={
            "reviewer": "delivery.director",
            "outcome": "accepted",
            "notes": "Pilot met quality and efficiency targets.",
            "action_owner": "enablement.lead",
        },
        headers=api_headers,
    )
    assert response.status_code == 201
    assert response.json()["outcome"] == "accepted"
