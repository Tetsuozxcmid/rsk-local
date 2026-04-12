from starlette.testclient import TestClient

from main import app


def test_openapi_schema_available():
    with TestClient(app) as client:
        response = client.get("/openapi.json")
    assert response.status_code == 200
    body = response.json()
    assert body.get("openapi")
    assert "paths" in body


def test_metrics_endpoint_returns_prometheus_text():
    with TestClient(app) as client:
        response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers.get("content-type", "")
    assert len(response.text) > 0
