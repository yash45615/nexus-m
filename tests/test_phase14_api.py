from fastapi.testclient import TestClient

from apps.api.main import app


client = TestClient(app)


def test_root():

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "NEXUS-M"


def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"


def test_openapi():

    response = client.get(
        "/openapi.json"
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        "NEXUS-M Analytical API"
        in data["info"]["title"]
    )


def test_kpis():

    response = client.get(
        "/api/v1/kpis"
    )

    assert response.status_code in [
        200,
        404,
    ]


def test_merchants():

    response = client.get(
        "/api/v1/merchants?page=1&page_size=5"
    )

    assert response.status_code in [
        200,
        404,
    ]


def test_partners():

    response = client.get(
        "/api/v1/partners?page=1&page_size=5"
    )

    assert response.status_code in [
        200,
        404,
    ]


def test_anomalies():

    response = client.get(
        "/api/v1/anomalies?page=1&page_size=5"
    )

    assert response.status_code in [
        200,
        404,
    ]


def test_opportunities():

    response = client.get(
        "/api/v1/opportunities?page=1&page_size=5"
    )

    assert response.status_code in [
        200,
        404,
    ]


def test_reconciliation():

    response = client.get(
        "/api/v1/reconciliation?page=1&page_size=5"
    )

    assert response.status_code in [
        200,
        404,
    ]