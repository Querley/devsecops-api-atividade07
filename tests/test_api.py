from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_security_headers_present():
    response = client.get("/health")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert "default-src 'self'" in response.headers.get("Content-Security-Policy", "")
    assert response.headers.get("Cache-Control") == "no-store"


def test_list_and_create_item():
    list_resp = client.get("/api/v1/items")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 2

    create_resp = client.post(
        "/api/v1/items",
        json={"name": "SBOM CycloneDX", "category": "Compliance", "price": 25.5},
    )
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["name"] == "SBOM CycloneDX"

    get_resp = client.get(f"/api/v1/items/{created['id']}")
    assert get_resp.status_code == 200


def test_item_validation_rejects_invalid_input():
    bad_resp = client.post(
        "/api/v1/items",
        json={"name": "<script>alert(1)</script>", "category": "XSS", "price": -5},
    )
    assert bad_resp.status_code == 422
