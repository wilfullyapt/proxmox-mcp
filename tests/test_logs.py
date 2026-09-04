"""Tests for self-logging / watchdog endpoints."""

from fastapi.testclient import TestClient

from main import app


def test_watchdog():
    with TestClient(app) as client:
        response = client.get("/logs/watchdog")
        assert response.status_code == 200
        data = response.json()
        assert "recent_errors" in data["data"]
        assert "status" in data["data"]


def test_recent_logs_filter():
    with TestClient(app) as client:
        response = client.get("/logs/recent?level=ERROR&lines=10")
        assert response.status_code == 200
        assert "logs" in response.json()["data"]
