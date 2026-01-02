"""
Exercise API tests.
"""

from fastapi.testclient import TestClient


# Exercise endpoint tests
def test_create_exercise(client: TestClient) -> None:
    """Test POST /api/v1/exercises/."""
    response = client.post(
        "/api/v1/exercises/",
        json={
            "name": "Chromatic Scale",
            "domains": ["Technique"],
            "instrument_compatibility": ["guitar", "bass"],
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Chromatic Scale"
    assert data["id"] is not None
    assert data["domains"] == ["Technique"]


def test_list_exercises(client: TestClient) -> None:
    """Test GET /api/v1/exercises/."""
    # Create test data
    client.post(
        "/api/v1/exercises/",
        json={
            "name": "Exercise 1",
            "domains": ["Technique"],
            "instrument_compatibility": None,
        },
    )
    client.post(
        "/api/v1/exercises/",
        json={
            "name": "Exercise 2",
            "domains": ["Harmony"],
            "instrument_compatibility": None,
        },
    )

    response = client.get("/api/v1/exercises/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Exercise 1"
    assert data[1]["name"] == "Exercise 2"


def test_list_exercises_with_pagination(client: TestClient) -> None:
    """Test GET /api/v1/exercises/ with skip and limit."""
    # Create multiple exercises
    for index in range(5):
        client.post(
            "/api/v1/exercises/",
            json={
                "name": f"Exercise {index}",
                "domains": ["Technique"],
                "instrument_compatibility": None,
            },
        )

    # Test skip and limit
    response = client.get("/api/v1/exercises/?skip=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Exercise 2"
    assert data[1]["name"] == "Exercise 3"


def test_get_exercise(client: TestClient) -> None:
    """Test GET /api/v1/exercises/{id}."""
    # Create exercise
    create_response = client.post(
        "/api/v1/exercises/",
        json={
            "name": "Test Exercise",
            "domains": ["Rhythm"],
            "instrument_compatibility": ["drums"],
        },
    )
    exercise_id = create_response.json()["id"]

    # Get exercise
    response = client.get(f"/api/v1/exercises/{exercise_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == exercise_id
    assert data["name"] == "Test Exercise"
    assert data["domains"] == ["Rhythm"]


def test_get_exercise_not_found(client: TestClient) -> None:
    """Test GET /api/v1/exercises/{id} with invalid ID."""
    response = client.get("/api/v1/exercises/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Exercise not found"


def test_update_exercise(client: TestClient) -> None:
    """Test PUT /api/v1/exercises/{id}."""
    # Create exercise
    create_response = client.post(
        "/api/v1/exercises/",
        json={
            "name": "Original Name",
            "domains": ["Technique"],
            "instrument_compatibility": None,
        },
    )
    exercise_id = create_response.json()["id"]

    # Update exercise
    response = client.put(
        f"/api/v1/exercises/{exercise_id}",
        json={
            "name": "Updated Name",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["domains"] == ["Technique"]  # Unchanged


def test_update_exercise_not_found(client: TestClient) -> None:
    """Test PUT /api/v1/exercises/{id} with invalid ID."""
    response = client.put(
        "/api/v1/exercises/999",
        json={"name": "Updated"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Exercise not found"


def test_delete_exercise(client: TestClient) -> None:
    """Test DELETE /api/v1/exercises/{id}."""
    # Create exercise
    create_response = client.post(
        "/api/v1/exercises/",
        json={
            "name": "To Delete",
            "domains": ["Technique"],
            "instrument_compatibility": None,
        },
    )
    exercise_id = create_response.json()["id"]

    # Delete exercise
    response = client.delete(f"/api/v1/exercises/{exercise_id}")
    assert response.status_code == 204

    # Verify deleted
    get_response = client.get(f"/api/v1/exercises/{exercise_id}")
    assert get_response.status_code == 404


def test_delete_exercise_not_found(client: TestClient) -> None:
    """Test DELETE /api/v1/exercises/{id} with invalid ID."""
    response = client.delete("/api/v1/exercises/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Exercise not found"


# Exercise state endpoint tests
def test_create_exercise_state(client: TestClient) -> None:
    """Test POST /api/v1/exercises/states/."""
    # First create an exercise
    exercise_response = client.post(
        "/api/v1/exercises/",
        json={
            "name": "State Test Exercise",
            "domains": ["Technique"],
            "instrument_compatibility": None,
        },
    )
    exercise_id = exercise_response.json()["id"]

    # Create exercise state
    response = client.post(
        "/api/v1/exercises/states/",
        json={
            "exercise_id": exercise_id,
            "last_practiced_date": "2025-01-15",
            "rolling_minutes_7d": 120,
            "rolling_minutes_28d": 480,
            "mastery_estimate": 0.65,
            "last_fatigue_profile": "F1",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["exercise_id"] == exercise_id
    assert data["rolling_minutes_7d"] == 120
    assert data["mastery_estimate"] == 0.65


def test_list_exercise_states(client: TestClient) -> None:
    """Test GET /api/v1/exercises/states/."""
    # Create exercises and states
    for index in range(2):
        exercise_response = client.post(
            "/api/v1/exercises/",
            json={
                "name": f"Exercise {index}",
                "domains": ["Technique"],
                "instrument_compatibility": None,
            },
        )
        exercise_id = exercise_response.json()["id"]

        client.post(
            "/api/v1/exercises/states/",
            json={
                "exercise_id": exercise_id,
                "rolling_minutes_7d": 100,
                "rolling_minutes_28d": 400,
                "mastery_estimate": 0.5,
                "last_fatigue_profile": None,
            },
        )

    response = client.get("/api/v1/exercises/states/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_list_exercise_states_with_pagination(client: TestClient) -> None:
    """Test GET /api/v1/exercises/states/ with skip and limit."""
    # Create multiple states
    for index in range(5):
        exercise_response = client.post(
            "/api/v1/exercises/",
            json={
                "name": f"Pagination Exercise {index}",
                "domains": ["Technique"],
                "instrument_compatibility": None,
            },
        )
        exercise_id = exercise_response.json()["id"]

        client.post(
            "/api/v1/exercises/states/",
            json={
                "exercise_id": exercise_id,
                "rolling_minutes_7d": 0,
                "rolling_minutes_28d": 0,
                "mastery_estimate": 0.0,
                "last_fatigue_profile": None,
            },
        )

    # Test skip and limit
    response = client.get("/api/v1/exercises/states/?skip=1&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_exercise_state(client: TestClient) -> None:
    """Test GET /api/v1/exercises/states/{id}."""
    # Create exercise and state
    exercise_response = client.post(
        "/api/v1/exercises/",
        json={
            "name": "Get State Exercise",
            "domains": ["Technique"],
            "instrument_compatibility": None,
        },
    )
    exercise_id = exercise_response.json()["id"]

    state_response = client.post(
        "/api/v1/exercises/states/",
        json={
            "exercise_id": exercise_id,
            "last_practiced_date": "2025-01-15",
            "rolling_minutes_7d": 90,
            "rolling_minutes_28d": 360,
            "mastery_estimate": 0.8,
            "last_fatigue_profile": "F2",
        },
    )
    state_id = state_response.json()["id"]

    # Get state
    response = client.get(f"/api/v1/exercises/states/{state_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == state_id
    assert data["mastery_estimate"] == 0.8


def test_get_exercise_state_not_found(client: TestClient) -> None:
    """Test GET /api/v1/exercises/states/{id} with invalid ID."""
    response = client.get("/api/v1/exercises/states/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Exercise state not found"


def test_update_exercise_state(client: TestClient) -> None:
    """Test PUT /api/v1/exercises/states/{id}."""
    # Create exercise and state
    exercise_response = client.post(
        "/api/v1/exercises/",
        json={
            "name": "Update State Exercise",
            "domains": ["Technique"],
            "instrument_compatibility": None,
        },
    )
    exercise_id = exercise_response.json()["id"]

    state_response = client.post(
        "/api/v1/exercises/states/",
        json={
            "exercise_id": exercise_id,
            "rolling_minutes_7d": 50,
            "rolling_minutes_28d": 200,
            "mastery_estimate": 0.3,
            "last_fatigue_profile": None,
        },
    )
    state_id = state_response.json()["id"]

    # Update state
    response = client.put(
        f"/api/v1/exercises/states/{state_id}",
        json={
            "mastery_estimate": 0.9,
            "last_fatigue_profile": "F1",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["mastery_estimate"] == 0.9
    assert data["last_fatigue_profile"] == "F1"
    assert data["rolling_minutes_7d"] == 50  # Unchanged


def test_update_exercise_state_not_found(client: TestClient) -> None:
    """Test PUT /api/v1/exercises/states/{id} with invalid ID."""
    response = client.put(
        "/api/v1/exercises/states/999",
        json={"mastery_estimate": 0.9},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Exercise state not found"


def test_delete_exercise_state(client: TestClient) -> None:
    """Test DELETE /api/v1/exercises/states/{id}."""
    # Create exercise and state
    exercise_response = client.post(
        "/api/v1/exercises/",
        json={
            "name": "Delete State Exercise",
            "domains": ["Technique"],
            "instrument_compatibility": None,
        },
    )
    exercise_id = exercise_response.json()["id"]

    state_response = client.post(
        "/api/v1/exercises/states/",
        json={
            "exercise_id": exercise_id,
            "rolling_minutes_7d": 0,
            "rolling_minutes_28d": 0,
            "mastery_estimate": 0.0,
            "last_fatigue_profile": None,
        },
    )
    state_id = state_response.json()["id"]

    # Delete state
    response = client.delete(f"/api/v1/exercises/states/{state_id}")
    assert response.status_code == 204

    # Verify deleted
    get_response = client.get(f"/api/v1/exercises/states/{state_id}")
    assert get_response.status_code == 404


def test_delete_exercise_state_not_found(client: TestClient) -> None:
    """Test DELETE /api/v1/exercises/states/{id} with invalid ID."""
    response = client.delete("/api/v1/exercises/states/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Exercise state not found"
