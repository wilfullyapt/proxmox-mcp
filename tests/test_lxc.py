"""Tests for LXC endpoints."""

from fastapi.testclient import TestClient

from main import app


def test_reverse_proxy_template():
    with TestClient(app) as client:
        response = client.get("/lxc/reverse-proxy-template?ostemplate=local:vztmpl/debian-12-standard_12.7-1_amd64.tar.zst")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "hostname" in data["data"]


def test_lxc_create_validation():
    """Test that invalid net0 is rejected."""
    with TestClient(app) as client:
        payload = {
            "node": "pve-01",
            "vmid": 210,
            "hostname": "test-proxy",
            "ostemplate": "local:vztmpl/debian-12-standard_12.7-1_amd64.tar.zst",
            "net0": "name=eth0,ip=dhcp"  # missing bridge
        }
        response = client.post("/lxc/create", json=payload)
        assert response.status_code == 422  # Pydantic validation error
