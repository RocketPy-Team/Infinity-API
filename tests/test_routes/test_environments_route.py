from unittest.mock import patch
import json
import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
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
def stub_env_summary():
    env_summary = EnvSummary()
    env_summary_json = env_summary.model_dump_json()
    return json.loads(env_summary_json)


def test_create_env(stub_env):
    with patch.object(
        EnvController, 'create_env', return_value=EnvCreated(env_id='123')
    ) as mock_create_env:
        response = client.post('/environments/', json=stub_env)
        assert response.status_code == 200
        assert response.json() == {
            'env_id': '123',
            'message': 'Environment successfully created',
        }
        mock_create_env.assert_called_once_with(Env(**stub_env))


def test_create_env_optional_params():
    test_object = {
        'latitude': 0,
        'longitude': 0,
        'elevation': 1,
        'atmospheric_model_type': 'STANDARD_ATMOSPHERE',
        'atmospheric_model_file': None,
        'date': '2021-01-01T00:00:00',
    }
    with patch.object(
        EnvController, 'create_env', return_value=EnvCreated(env_id='123')
    ) as mock_create_env:
        response = client.post('/environments/', json=test_object)
        assert response.status_code == 200
        assert response.json() == {
            'env_id': '123',
            'message': 'Environment successfully created',
        }
        mock_create_env.assert_called_once_with(Env(**test_object))


def test_create_env_invalid_input():
    response = client.post(
        '/environments/', json={'latitude': 'foo', 'longitude': 'bar'}
    )
    assert response.status_code == 422


def test_create_env_server_error(stub_env):
    with patch.object(
        EnvController,
        'create_env',
        side_effect=HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    ):
        response = client.post('/environments/', json=stub_env)
        assert response.status_code == 500
        assert response.json() == {'detail': 'Internal Server Error'}


def test_read_env(stub_env):
    with patch.object(
        EnvController, 'get_env_by_id', return_value=Env(**stub_env)
    ) as mock_read_env:
        response = client.get('/environments/123')
        assert response.status_code == 200
        assert response.json() == stub_env
        mock_read_env.assert_called_once_with('123')


def test_read_env_not_found():
    with patch.object(
        EnvController,
        'get_env_by_id',
        side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND),
    ) as mock_read_env:
        response = client.get('/environments/123')
        assert response.status_code == 404
        assert response.json() == {'detail': 'Not Found'}
        mock_read_env.assert_called_once_with('123')


def test_read_env_server_error():
    with patch.object(
        EnvController,
        'get_env_by_id',
        side_effect=HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    ):
        response = client.get('/environments/123')
        assert response.status_code == 500
        assert response.json() == {'detail': 'Internal Server Error'}


def test_update_env(stub_env):
    with patch.object(
        EnvController,
        'update_env_by_id',
        return_value=EnvUpdated(env_id='123'),
    ) as mock_update_env:
        response = client.put('/environments/123', json=stub_env)
        assert response.status_code == 200
        assert response.json() == {
            'env_id': '123',
            'message': 'Environment successfully updated',
        }
        mock_update_env.assert_called_once_with('123', Env(**stub_env))


def test_update_env_invalid_input():
    response = client.put(
        '/environments/123', json={'latitude': 'foo', 'longitude': 'bar'}
    )
    assert response.status_code == 422


def test_update_env_not_found(stub_env):
    with patch.object(
        EnvController,
        'update_env_by_id',
        side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND),
    ):
        response = client.put('/environments/123', json=stub_env)
        assert response.status_code == 404
        assert response.json() == {'detail': 'Not Found'}


def test_update_env_server_error(stub_env):
    with patch.object(
        EnvController,
        'update_env_by_id',
        side_effect=HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    ):
        response = client.put('/environments/123', json=stub_env)
        assert response.status_code == 500
        assert response.json() == {'detail': 'Internal Server Error'}


def test_delete_env():
    with patch.object(
        EnvController,
        'delete_env_by_id',
        return_value=EnvDeleted(env_id='123'),
    ) as mock_delete_env:
        response = client.delete('/environments/123')
        assert response.status_code == 200
        assert response.json() == {
            'env_id': '123',
            'message': 'Environment successfully deleted',
        }
        mock_delete_env.assert_called_once_with('123')


def test_delete_env_server_error():
    with patch.object(
        EnvController,
        'delete_env_by_id',
        side_effect=HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    ):
        response = client.delete('/environments/123')
        assert response.status_code == 500
        assert response.json() == {'detail': 'Internal Server Error'}


def test_simulate_env(stub_env_summary):
    with patch.object(
        EnvController,
        'simulate_env',
        return_value=EnvSummary(**stub_env_summary),
    ) as mock_simulate_env:
        response = client.get('/environments/123/summary')
        assert response.status_code == 200
        assert response.json() == stub_env_summary
        mock_simulate_env.assert_called_once_with('123')


def test_simulate_env_not_found():
    with patch.object(
        EnvController,
        'simulate_env',
        side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND),
    ) as mock_simulate_env:
        response = client.get('/environments/123/summary')
        assert response.status_code == 404
        assert response.json() == {'detail': 'Not Found'}
        mock_simulate_env.assert_called_once_with('123')


def test_simulate_env_server_error():
    with patch.object(
        EnvController,
        'simulate_env',
        side_effect=HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    ):
        response = client.get('/environments/123/summary')
        assert response.status_code == 500
        assert response.json() == {'detail': 'Internal Server Error'}


def test_read_rocketpy_env():
    with patch.object(
        EnvController, 'get_rocketpy_env_binary', return_value=b'rocketpy'
    ) as mock_read_rocketpy_env:
        response = client.get('/environments/123/rocketpy')
        assert response.status_code == 203
        assert response.content == b'rocketpy'
        assert response.headers['content-type'] == 'application/octet-stream'
        mock_read_rocketpy_env.assert_called_once_with('123')


def test_read_rocketpy_env_not_found():
    with patch.object(
        EnvController,
        'get_rocketpy_env_binary',
        side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND),
    ) as mock_read_rocketpy_env:
        response = client.get('/environments/123/rocketpy')
        assert response.status_code == 404
        assert response.json() == {'detail': 'Not Found'}
        mock_read_rocketpy_env.assert_called_once_with('123')


def test_read_rocketpy_env_server_error():
    with patch.object(
        EnvController,
        'get_rocketpy_env_binary',
        side_effect=HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    ):
        response = client.get('/environments/123/rocketpy')
        assert response.status_code == 500
        assert response.json() == {'detail': 'Internal Server Error'}
