import os
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient

from main import app
from routers.admin import get_api_key  # if needed for override


@pytest.fixture(autouse=True)
def set_test_api_key():
    os.environ["MCP_API_KEY"] = "test-key"
    yield
    os.environ.pop("MCP_API_KEY", None)


def override_get_api_key():
    return "test-key"


app.dependency_overrides = {}


@patch("routers.admin.subprocess.run")
@patch("routers.admin.subprocess.Popen")
def test_admin_update_success(mock_popen, mock_run):
    """Test that /admin/update triggers the expected commands and returns success."""
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    mock_popen.return_value = MagicMock()

    # Override the key check for the test
    from routers.admin import trigger_update
    app.dependency_overrides = {}

    client = TestClient(app)
    payload = {"ref": "origin/main", "force": False}

    response = client.post(
        "/admin/update",
        json=payload,
        headers={"X-API-Key": "test-key"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Update to origin/main completed" in data["data"]["message"]


def test_admin_update_requires_key():
    """Without the correct key the endpoint should reject the request."""
    client = TestClient(app)
    payload = {"ref": "origin/main"}

    response = client.post("/admin/update", json=payload)  # no header
    assert response.status_code in (401, 403)
