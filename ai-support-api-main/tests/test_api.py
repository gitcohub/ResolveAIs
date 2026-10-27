from fastapi.testclient import TestClient
from app.config import get_settings
from app.main import app
client = TestClient(app)
AUTH_HEADERS = {
    "X-API-Key": get_settings().app_api_key,
}
def test_health_check() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "ai_mode": "mock",
    }
def test_protected_endpoint_requires_api_key() -> None:
    response = client.post(
        "/support/analyze",
        json={
            "message": "My order has not arrived yet.",
            "priority": "normal",
        },
    )
    assert response.status_code == 401
    assert response.json() == {
        "detail": "API key is required.",
    }
def test_rejects_invalid_api_key() -> None:
    response = client.post(
        "/support/analyze",
        headers={"X-API-Key": "wrong-key"},
        json={
            "message": "My order has not arrived yet.",
            "priority": "normal",
        },
    )
    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid API key.",
    }
def test_analyze_shipping_request() -> None:
    response = client.post(
        "/support/analyze",
        headers=AUTH_HEADERS,
        json={
            "message": "My order has not arrived yet.",
            "priority": "normal",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "shipping"
    assert body["priority"] == "normal"
    assert body["processing_mode"] == "mock"
    assert body["suggested_reply"]
def test_rejects_invalid_request() -> None:
    response = client.post(
        "/support/analyze",
        headers=AUTH_HEADERS,
        json={
            "message": "hi",
            "priority": "urgent",
        },
    )
    assert response.status_code == 422
def test_background_support_job() -> None:
    submit_response = client.post(
        "/support/jobs",
        headers=AUTH_HEADERS,
        json={
            "message": "My delivery is late and I need an update.",
            "priority": "high",
        },
    )
    assert submit_response.status_code == 202
    submitted_job = submit_response.json()
    assert submitted_job["status"] == "queued"
    assert submitted_job["job_id"]
    assert submitted_job["status_url"].endswith(
        submitted_job["job_id"]
    )
    status_response = client.get(
        submitted_job["status_url"],
        headers=AUTH_HEADERS,
    )
    assert status_response.status_code == 200
    completed_job = status_response.json()
    assert completed_job["status"] == "completed"
    assert completed_job["result"]["category"] == "shipping"
    assert completed_job["result"]["priority"] == "high"
    assert completed_job["result"]["processing_mode"] == "mock"
    assert completed_job["error"] is None
def test_unknown_background_job_returns_404() -> None:
    response = client.get(
        "/support/jobs/not-a-real-job-id",
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Job not found.",
    }
