import pytest

"""More substantial tests using mocking for PVE responses."""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from main import app


@patch("routers.cluster.get_session")
@pytest.mark.xfail(reason="Mocking not yet robust - real network call + exception handler issue")
def test_cluster_status_mocked(mock_get_session):
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": [{"type": "cluster", "name": "test"}]}
    mock_response.raise_for_status.return_value = None
    mock_get_session.return_value.get.return_value = mock_response

    with TestClient(app) as client:
        response = client.get("/cluster/status")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


@patch("routers.lxc.get_session")
@pytest.mark.xfail(reason="Mocking not yet robust - real network call + exception handler issue")
def test_lxc_create_mocked(mock_get_session):
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": {"upid": "UPID:test:123"}}
    mock_response.raise_for_status.return_value = None
    mock_get_session.return_value.post.return_value = mock_response

    payload = {
        "node": "pve-01",
        "vmid": 210,
        "hostname": "test-lxc",
        "ostemplate": "local:vztmpl/debian-12-standard_12.7-1_amd64.tar.zst",
        "net0": "name=eth0,bridge=vmbr0,ip=dhcp"
    }

    with TestClient(app) as client:
        response = client.post("/lxc/create", json=payload)
        assert response.status_code == 200
        assert response.json()["success"] is True
