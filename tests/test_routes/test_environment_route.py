from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from lib.models.environment import Env
from lib.controllers.environment import EnvController
from lib.views.environment import (
    EnvCreated,
    EnvUpdated,
    EnvDeleted,
    EnvSummary,
)
from lib import app

client = TestClient(app)


@pytest.fixture
def mock_env():
    return Env(latitude=0, longitude=0)


@pytest.fixture
def mock_env_summary():
    return EnvSummary()


def test_create_env():
    with patch.object(
        EnvController, "create_env", return_value=EnvCreated(env_id="123")
    ) as mock_create_env:
        response = client.post(
            "/environments/", json={"latitude": 0, "longitude": 0}
        )
        assert response.status_code == 200
        assert response.json() == {
            "env_id": "123",
            "message": "Environment successfully created",
        }
        mock_create_env.assert_called_once_with(Env(latitude=0, longitude=0))


def test_read_env(mock_env):
    with patch.object(
        EnvController, "get_env_by_id", return_value=mock_env
    ) as mock_read_env:
        response = client.get("/environments/123")
        assert response.status_code == 200
        expected_content = mock_env.model_dump()
        expected_content["date"] = expected_content["date"].isoformat()
        assert response.json() == expected_content
        mock_read_env.assert_called_once_with("123")


def test_update_env():
    with patch.object(
        EnvController,
        "update_env_by_id",
        return_value=EnvUpdated(env_id="123"),
    ) as mock_update_env:
        response = client.put(
            "/environments/123", json={"longitude": 1, "latitude": 1}
        )
        assert response.status_code == 200
        assert response.json() == {
            "env_id": "123",
            "message": "Environment successfully updated",
        }
        mock_update_env.assert_called_once_with(
            "123", Env(latitude=1, longitude=1)
        )


def test_delete_env():
    with patch.object(
        EnvController,
        "delete_env_by_id",
        return_value=EnvDeleted(env_id="123"),
    ) as mock_delete_env:
        response = client.delete("/environments/123")
        assert response.status_code == 200
        assert response.json() == {
            "env_id": "123",
            "message": "Environment successfully deleted",
        }
        mock_delete_env.assert_called_once_with("123")


def test_simulate_env(mock_env_summary):
    with patch.object(
        EnvController, "simulate_env", return_value=mock_env_summary
    ) as mock_simulate_env:
        response = client.get("/environments/123/summary")
        assert response.status_code == 200
        expected_content = mock_env_summary.model_dump()
        expected_content["date"] = expected_content["date"].isoformat()
        expected_content["local_date"] = expected_content[
            "local_date"
        ].isoformat()
        expected_content["datetime_date"] = expected_content[
            "datetime_date"
        ].isoformat()
        assert response.json() == expected_content
        mock_simulate_env.assert_called_once_with("123")


def test_read_rocketpy_env():
    with patch.object(
        EnvController, "get_rocketpy_env_binary", return_value=b'rocketpy'
    ) as mock_read_rocketpy_env:
        response = client.get("/environments/123/rocketpy")
        assert response.status_code == 203
        assert response.content == b'rocketpy'
        assert response.headers["content-type"] == "application/octet-stream"
        mock_read_rocketpy_env.assert_called_once_with("123")
