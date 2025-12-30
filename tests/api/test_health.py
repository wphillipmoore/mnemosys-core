"""
Health check endpoint tests.
"""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


def test_health_check_basic(client: TestClient) -> None:
    """Test basic health check endpoint."""
    response = client.get("/health/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_database_health_success(client: TestClient) -> None:
    """Test database health check with successful connection."""
    response = client.get("/health/db")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"


def test_database_health_failure(client: TestClient) -> None:
    """Test database health check with connection failure."""
    # Mock the database session to raise an exception
    with patch("mnemosys_core.api.routers.health.get_db") as mock_get_db:
        mock_session = MagicMock()
        mock_session.execute.side_effect = Exception("Connection failed")
        mock_get_db.return_value = mock_session

        # We need to override the dependency in the client
        def failing_db() -> MagicMock:
            return mock_session

        # Create a new client with overridden dependency
        from mnemosys_core.api.app import create_app
        from mnemosys_core.api.dependencies import get_db
        from mnemosys_core.db.engine import create_db_engine

        engine = create_db_engine("sqlite:///:memory:", echo=False)
        app = create_app(engine)
        app.dependency_overrides[get_db] = failing_db

        test_client = TestClient(app)
        response = test_client.get("/health/db")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert "Connection failed" in data["database"]
