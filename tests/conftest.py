import os
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

TEST_DB = Path("/tmp/control_plane_test.db")
TEST_DB.unlink(missing_ok=True)
os.environ["CONTROL_PLANE_DATABASE_URL"] = f"sqlite:///{TEST_DB}"
os.environ["CONTROL_PLANE_API_KEY"] = "test-key"
os.environ["CONTROL_PLANE_SEED_DEMO_DATA"] = "false"

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def reset_database() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def api_headers() -> dict[str, str]:
    return {"X-API-Key": "test-key"}
