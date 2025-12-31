"""
Instrument API tests.
"""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    """Test basic health check endpoint."""
    response = client.get("/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_instrument(client: TestClient) -> None:
    """Test POST /api/v1/instruments/."""
    response = client.post(
        "/api/v1/instruments/",
        json={
            "name": "Test Guitar",
            "string_count": 6,
            "scale_length": 25.5,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Guitar"
    assert data["id"] is not None


def test_list_instruments(client: TestClient) -> None:
    """Test GET /api/v1/instruments/."""
    # Create test data
    client.post(
        "/api/v1/instruments/",
        json={
            "name": "Guitar 1",
            "string_count": 6,
        },
    )

    response = client.get("/api/v1/instruments/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Guitar 1"


def test_get_instrument(client: TestClient) -> None:
    """Test GET /api/v1/instruments/{id}."""
    # Create instrument
    create_response = client.post(
        "/api/v1/instruments/",
        json={
            "name": "Test Bass",
            "string_count": 4,
        },
    )
    instrument_id = create_response.json()["id"]

    # Get instrument
    response = client.get(f"/api/v1/instruments/{instrument_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == instrument_id
    assert data["name"] == "Test Bass"


def test_get_instrument_not_found(client: TestClient) -> None:
    """Test GET /api/v1/instruments/{id} with invalid ID."""
    response = client.get("/api/v1/instruments/999")
    assert response.status_code == 404


def test_update_instrument(client: TestClient) -> None:
    """Test PUT /api/v1/instruments/{id}."""
    # Create instrument
    create_response = client.post(
        "/api/v1/instruments/",
        json={
            "name": "Original Name",
            "string_count": 6,
        },
    )
    instrument_id = create_response.json()["id"]

    # Update instrument
    response = client.put(
        f"/api/v1/instruments/{instrument_id}",
        json={"name": "Updated Name"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"


def test_update_instrument_not_found(client: TestClient) -> None:
    """Test PUT /api/v1/instruments/{id} with invalid ID."""
    response = client.put(
        "/api/v1/instruments/999",
        json={"name": "Updated"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Instrument not found"


def test_delete_instrument_not_found(client: TestClient) -> None:
    """Test DELETE /api/v1/instruments/{id} with invalid ID."""
    response = client.delete("/api/v1/instruments/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Instrument not found"


def test_delete_instrument(client: TestClient) -> None:
    """Test DELETE /api/v1/instruments/{id}."""
    # Create instrument
    create_response = client.post(
        "/api/v1/instruments/",
        json={
            "name": "To Delete",
            "string_count": 6,
        },
    )
    instrument_id = create_response.json()["id"]

    # Delete instrument
    response = client.delete(f"/api/v1/instruments/{instrument_id}")
    assert response.status_code == 204

    # Verify deleted
    get_response = client.get(f"/api/v1/instruments/{instrument_id}")
    assert get_response.status_code == 404
