"""
Session API tests.
"""

from typing import Any

from fastapi.testclient import TestClient


# Helper function to create required dependencies
def create_test_instrument(client: TestClient) -> int:
    """Create a test instrument and return its ID."""
    response = client.post(
        "/api/v1/instruments/",
        json={
            "name": "Test Guitar",
            "string_count": 6,
            "scale_length": 25.5,
        },
    )
    data: dict[str, Any] = response.json()
    return int(data["id"])


def create_test_exercise(client: TestClient) -> int:
    """Create a test exercise and return its ID."""
    response = client.post(
        "/api/v1/exercises/",
        json={
            "name": "Test Exercise",
            "domains": ["Technique"],
            "instrument_compatibility": None,
        },
    )
    data: dict[str, Any] = response.json()
    return int(data["id"])


# Session endpoint tests
def test_create_session(client: TestClient) -> None:
    """Test POST /api/v1/sessions/."""
    instrument_id = create_test_instrument(client)

    response = client.post(
        "/api/v1/sessions/",
        json={
            "instrument_id": instrument_id,
            "session_date": "2025-01-15",
            "session_type": "normal",
            "total_minutes": 60,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["instrument_id"] == instrument_id
    assert data["session_date"] == "2025-01-15"
    assert data["session_type"] == "normal"
    assert data["total_minutes"] == 60


def test_list_sessions(client: TestClient) -> None:
    """Test GET /api/v1/sessions/."""
    instrument_id = create_test_instrument(client)

    # Create test sessions
    client.post(
        "/api/v1/sessions/",
        json={
            "instrument_id": instrument_id,
            "session_date": "2025-01-15",
            "session_type": "normal",
            "total_minutes": 45,
        },
    )
    client.post(
        "/api/v1/sessions/",
        json={
            "instrument_id": instrument_id,
            "session_date": "2025-01-16",
            "session_type": "light",
            "total_minutes": 30,
        },
    )

    response = client.get("/api/v1/sessions/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_list_sessions_with_pagination(client: TestClient) -> None:
    """Test GET /api/v1/sessions/ with skip and limit."""
    instrument_id = create_test_instrument(client)

    # Create multiple sessions
    for i in range(5):
        client.post(
            "/api/v1/sessions/",
            json={
                "instrument_id": instrument_id,
                "session_date": f"2025-01-{15+i:02d}",
                "session_type": "normal",
                "total_minutes": 30,
            },
        )

    # Test skip and limit
    response = client.get("/api/v1/sessions/?skip=1&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_session(client: TestClient) -> None:
    """Test GET /api/v1/sessions/{id}."""
    instrument_id = create_test_instrument(client)

    create_response = client.post(
        "/api/v1/sessions/",
        json={
            "instrument_id": instrument_id,
            "session_date": "2025-01-15",
            "session_type": "heavy",
            "total_minutes": 90,
        },
    )
    session_id = create_response.json()["id"]

    response = client.get(f"/api/v1/sessions/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == session_id
    assert data["session_type"] == "heavy"


def test_get_session_not_found(client: TestClient) -> None:
    """Test GET /api/v1/sessions/{id} with invalid ID."""
    response = client.get("/api/v1/sessions/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


def test_update_session(client: TestClient) -> None:
    """Test PUT /api/v1/sessions/{id}."""
    instrument_id = create_test_instrument(client)

    create_response = client.post(
        "/api/v1/sessions/",
        json={
            "instrument_id": instrument_id,
            "session_date": "2025-01-15",
            "session_type": "normal",
            "total_minutes": 60,
        },
    )
    session_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/sessions/{session_id}",
        json={
            "total_minutes": 75,
            "session_type": "heavy",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_minutes"] == 75
    assert data["session_type"] == "heavy"


def test_update_session_not_found(client: TestClient) -> None:
    """Test PUT /api/v1/sessions/{id} with invalid ID."""
    response = client.put(
        "/api/v1/sessions/999",
        json={"total_minutes": 75},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


def test_delete_session(client: TestClient) -> None:
    """Test DELETE /api/v1/sessions/{id}."""
    instrument_id = create_test_instrument(client)

    create_response = client.post(
        "/api/v1/sessions/",
        json={
            "instrument_id": instrument_id,
            "session_date": "2025-01-15",
            "session_type": "normal",
            "total_minutes": 60,
        },
    )
    session_id = create_response.json()["id"]

    response = client.delete(f"/api/v1/sessions/{session_id}")
    assert response.status_code == 204

    # Verify deleted
    get_response = client.get(f"/api/v1/sessions/{session_id}")
    assert get_response.status_code == 404


def test_delete_session_not_found(client: TestClient) -> None:
    """Test DELETE /api/v1/sessions/{id} with invalid ID."""
    response = client.delete("/api/v1/sessions/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


# Session block endpoint tests
def test_create_session_block(client: TestClient) -> None:
    """Test POST /api/v1/sessions/blocks/."""
    instrument_id = create_test_instrument(client)
    exercise_id = create_test_exercise(client)

    session_response = client.post(
        "/api/v1/sessions/",
        json={
            "instrument_id": instrument_id,
            "session_date": "2025-01-15",
            "session_type": "normal",
            "total_minutes": 60,
        },
    )
    session_id = session_response.json()["id"]

    response = client.post(
        "/api/v1/sessions/blocks/",
        json={
            "practice_id": session_id,
            "exercise_id": exercise_id,
            "block_order": 1,
            "block_type": "Warmup",
            "duration_minutes": 15,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["practice_id"] == session_id
    assert data["exercise_id"] == exercise_id
    assert data["block_order"] == 1
    assert data["block_type"] == "Warmup"


def test_list_session_blocks(client: TestClient) -> None:
    """Test GET /api/v1/sessions/blocks/."""
    instrument_id = create_test_instrument(client)
    exercise_id = create_test_exercise(client)

    session_response = client.post(
        "/api/v1/sessions/",
        json={
            "instrument_id": instrument_id,
            "session_date": "2025-01-15",
            "session_type": "normal",
            "total_minutes": 60,
        },
    )
    session_id = session_response.json()["id"]

    # Create blocks
    for i in range(2):
        client.post(
            "/api/v1/sessions/blocks/",
            json={
                "practice_id": session_id,
                "exercise_id": exercise_id,
                "block_order": i + 1,
                "block_type": "Technique",
                "duration_minutes": 20,
            },
        )

    response = client.get("/api/v1/sessions/blocks/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_list_session_blocks_with_pagination(client: TestClient) -> None:
    """Test GET /api/v1/sessions/blocks/ with skip and limit."""
    instrument_id = create_test_instrument(client)
    exercise_id = create_test_exercise(client)

    session_response = client.post(
        "/api/v1/sessions/",
        json={
            "instrument_id": instrument_id,
            "session_date": "2025-01-15",
            "session_type": "normal",
            "total_minutes": 60,
        },
    )
    session_id = session_response.json()["id"]

    # Create multiple blocks
    for i in range(5):
        client.post(
            "/api/v1/sessions/blocks/",
            json={
                "practice_id": session_id,
                "exercise_id": exercise_id,
                "block_order": i + 1,
                "block_type": "Technique",
                "duration_minutes": 10,
            },
        )

    response = client.get("/api/v1/sessions/blocks/?skip=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_session_block(client: TestClient) -> None:
    """Test GET /api/v1/sessions/blocks/{id}."""
    instrument_id = create_test_instrument(client)
    exercise_id = create_test_exercise(client)

    session_response = client.post(
        "/api/v1/sessions/",
        json={
            "instrument_id": instrument_id,
            "session_date": "2025-01-15",
            "session_type": "normal",
            "total_minutes": 60,
        },
    )
    session_id = session_response.json()["id"]

    block_response = client.post(
        "/api/v1/sessions/blocks/",
        json={
            "practice_id": session_id,
            "exercise_id": exercise_id,
            "block_order": 1,
            "block_type": "Harmony",
            "duration_minutes": 25,
        },
    )
    block_id = block_response.json()["id"]

    response = client.get(f"/api/v1/sessions/blocks/{block_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == block_id
    assert data["block_type"] == "Harmony"


def test_get_session_block_not_found(client: TestClient) -> None:
    """Test GET /api/v1/sessions/blocks/{id} with invalid ID."""
    response = client.get("/api/v1/sessions/blocks/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Session block not found"


def test_update_session_block(client: TestClient) -> None:
    """Test PUT /api/v1/sessions/blocks/{id}."""
    instrument_id = create_test_instrument(client)
    exercise_id = create_test_exercise(client)

    session_response = client.post(
        "/api/v1/sessions/",
        json={
            "instrument_id": instrument_id,
            "session_date": "2025-01-15",
            "session_type": "normal",
            "total_minutes": 60,
        },
    )
    session_id = session_response.json()["id"]

    block_response = client.post(
        "/api/v1/sessions/blocks/",
        json={
            "practice_id": session_id,
            "exercise_id": exercise_id,
            "block_order": 1,
            "block_type": "Warmup",
            "duration_minutes": 15,
        },
    )
    block_id = block_response.json()["id"]

    response = client.put(
        f"/api/v1/sessions/blocks/{block_id}",
        json={
            "duration_minutes": 20,
            "block_type": "Technique",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["duration_minutes"] == 20
    assert data["block_type"] == "Technique"


def test_update_session_block_not_found(client: TestClient) -> None:
    """Test PUT /api/v1/sessions/blocks/{id} with invalid ID."""
    response = client.put(
        "/api/v1/sessions/blocks/999",
        json={"duration_minutes": 20},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Session block not found"


def test_delete_session_block(client: TestClient) -> None:
    """Test DELETE /api/v1/sessions/blocks/{id}."""
    instrument_id = create_test_instrument(client)
    exercise_id = create_test_exercise(client)

    session_response = client.post(
        "/api/v1/sessions/",
        json={
            "instrument_id": instrument_id,
            "session_date": "2025-01-15",
            "session_type": "normal",
            "total_minutes": 60,
        },
    )
    session_id = session_response.json()["id"]

    block_response = client.post(
        "/api/v1/sessions/blocks/",
        json={
            "practice_id": session_id,
            "exercise_id": exercise_id,
            "block_order": 1,
            "block_type": "Warmup",
            "duration_minutes": 15,
        },
    )
    block_id = block_response.json()["id"]

    response = client.delete(f"/api/v1/sessions/blocks/{block_id}")
    assert response.status_code == 204

    # Verify deleted
    get_response = client.get(f"/api/v1/sessions/blocks/{block_id}")
    assert get_response.status_code == 404


def test_delete_session_block_not_found(client: TestClient) -> None:
    """Test DELETE /api/v1/sessions/blocks/{id} with invalid ID."""
    response = client.delete("/api/v1/sessions/blocks/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Session block not found"


# Block log endpoint tests
def test_create_block_log(client: TestClient) -> None:
    """Test POST /api/v1/sessions/logs/."""
    instrument_id = create_test_instrument(client)
    exercise_id = create_test_exercise(client)

    session_response = client.post(
        "/api/v1/sessions/",
        json={
            "instrument_id": instrument_id,
            "session_date": "2025-01-15",
            "session_type": "normal",
            "total_minutes": 60,
        },
    )
    session_id = session_response.json()["id"]

    block_response = client.post(
        "/api/v1/sessions/blocks/",
        json={
            "practice_id": session_id,
            "exercise_id": exercise_id,
            "block_order": 1,
            "block_type": "Warmup",
            "duration_minutes": 15,
        },
    )
    block_id = block_response.json()["id"]

    response = client.post(
        "/api/v1/sessions/logs/",
        json={
            "practice_block_id": block_id,
            "completed": "yes",
            "quality": "clean",
            "notes": "Felt great today",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["practice_block_id"] == block_id
    assert data["completed"] == "yes"
    assert data["quality"] == "clean"
    assert data["notes"] == "Felt great today"


def test_list_block_logs(client: TestClient) -> None:
    """Test GET /api/v1/sessions/logs/."""
    instrument_id = create_test_instrument(client)
    exercise_id = create_test_exercise(client)

    session_response = client.post(
        "/api/v1/sessions/",
        json={
            "instrument_id": instrument_id,
            "session_date": "2025-01-15",
            "session_type": "normal",
            "total_minutes": 60,
        },
    )
    session_id = session_response.json()["id"]

    block_response = client.post(
        "/api/v1/sessions/blocks/",
        json={
            "practice_id": session_id,
            "exercise_id": exercise_id,
            "block_order": 1,
            "block_type": "Warmup",
            "duration_minutes": 15,
        },
    )
    block_id = block_response.json()["id"]

    # Create logs
    for _ in range(2):
        client.post(
            "/api/v1/sessions/logs/",
            json={
                "practice_block_id": block_id,
                "completed": "yes",
                "quality": "clean",
                "notes": None,
            },
        )

    response = client.get("/api/v1/sessions/logs/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_list_block_logs_with_pagination(client: TestClient) -> None:
    """Test GET /api/v1/sessions/logs/ with skip and limit."""
    instrument_id = create_test_instrument(client)
    exercise_id = create_test_exercise(client)

    session_response = client.post(
        "/api/v1/sessions/",
        json={
            "instrument_id": instrument_id,
            "session_date": "2025-01-15",
            "session_type": "normal",
            "total_minutes": 60,
        },
    )
    session_id = session_response.json()["id"]

    block_response = client.post(
        "/api/v1/sessions/blocks/",
        json={
            "practice_id": session_id,
            "exercise_id": exercise_id,
            "block_order": 1,
            "block_type": "Warmup",
            "duration_minutes": 15,
        },
    )
    block_id = block_response.json()["id"]

    # Create multiple logs
    for _ in range(5):
        client.post(
            "/api/v1/sessions/logs/",
            json={
                "practice_block_id": block_id,
                "completed": "yes",
                "quality": "clean",
                "notes": None,
            },
        )

    response = client.get("/api/v1/sessions/logs/?skip=1&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_block_log(client: TestClient) -> None:
    """Test GET /api/v1/sessions/logs/{id}."""
    instrument_id = create_test_instrument(client)
    exercise_id = create_test_exercise(client)

    session_response = client.post(
        "/api/v1/sessions/",
        json={
            "instrument_id": instrument_id,
            "session_date": "2025-01-15",
            "session_type": "normal",
            "total_minutes": 60,
        },
    )
    session_id = session_response.json()["id"]

    block_response = client.post(
        "/api/v1/sessions/blocks/",
        json={
            "practice_id": session_id,
            "exercise_id": exercise_id,
            "block_order": 1,
            "block_type": "Warmup",
            "duration_minutes": 15,
        },
    )
    block_id = block_response.json()["id"]

    log_response = client.post(
        "/api/v1/sessions/logs/",
        json={
            "practice_block_id": block_id,
            "completed": "partial",
            "quality": "acceptable",
            "notes": "Had some difficulties",
        },
    )
    log_id = log_response.json()["id"]

    response = client.get(f"/api/v1/sessions/logs/{log_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == log_id
    assert data["completed"] == "partial"
    assert data["quality"] == "acceptable"


def test_get_block_log_not_found(client: TestClient) -> None:
    """Test GET /api/v1/sessions/logs/{id} with invalid ID."""
    response = client.get("/api/v1/sessions/logs/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Block log not found"


def test_update_block_log(client: TestClient) -> None:
    """Test PUT /api/v1/sessions/logs/{id}."""
    instrument_id = create_test_instrument(client)
    exercise_id = create_test_exercise(client)

    session_response = client.post(
        "/api/v1/sessions/",
        json={
            "instrument_id": instrument_id,
            "session_date": "2025-01-15",
            "session_type": "normal",
            "total_minutes": 60,
        },
    )
    session_id = session_response.json()["id"]

    block_response = client.post(
        "/api/v1/sessions/blocks/",
        json={
            "practice_id": session_id,
            "exercise_id": exercise_id,
            "block_order": 1,
            "block_type": "Warmup",
            "duration_minutes": 15,
        },
    )
    block_id = block_response.json()["id"]

    log_response = client.post(
        "/api/v1/sessions/logs/",
        json={
            "practice_block_id": block_id,
            "completed": "no",
            "quality": "sloppy",
            "notes": "Tired",
        },
    )
    log_id = log_response.json()["id"]

    response = client.put(
        f"/api/v1/sessions/logs/{log_id}",
        json={
            "completed": "yes",
            "quality": "clean",
            "notes": "Actually did well",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["completed"] == "yes"
    assert data["quality"] == "clean"
    assert data["notes"] == "Actually did well"


def test_update_block_log_not_found(client: TestClient) -> None:
    """Test PUT /api/v1/sessions/logs/{id} with invalid ID."""
    response = client.put(
        "/api/v1/sessions/logs/999",
        json={"completed": "yes"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Block log not found"


def test_delete_block_log(client: TestClient) -> None:
    """Test DELETE /api/v1/sessions/logs/{id}."""
    instrument_id = create_test_instrument(client)
    exercise_id = create_test_exercise(client)

    session_response = client.post(
        "/api/v1/sessions/",
        json={
            "instrument_id": instrument_id,
            "session_date": "2025-01-15",
            "session_type": "normal",
            "total_minutes": 60,
        },
    )
    session_id = session_response.json()["id"]

    block_response = client.post(
        "/api/v1/sessions/blocks/",
        json={
            "practice_id": session_id,
            "exercise_id": exercise_id,
            "block_order": 1,
            "block_type": "Warmup",
            "duration_minutes": 15,
        },
    )
    block_id = block_response.json()["id"]

    log_response = client.post(
        "/api/v1/sessions/logs/",
        json={
            "practice_block_id": block_id,
            "completed": "yes",
            "quality": "clean",
            "notes": None,
        },
    )
    log_id = log_response.json()["id"]

    response = client.delete(f"/api/v1/sessions/logs/{log_id}")
    assert response.status_code == 204

    # Verify deleted
    get_response = client.get(f"/api/v1/sessions/logs/{log_id}")
    assert get_response.status_code == 404


def test_delete_block_log_not_found(client: TestClient) -> None:
    """Test DELETE /api/v1/sessions/logs/{id} with invalid ID."""
    response = client.delete("/api/v1/sessions/logs/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Block log not found"
