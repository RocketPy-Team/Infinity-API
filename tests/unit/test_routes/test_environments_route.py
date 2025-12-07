from unittest.mock import patch, Mock, AsyncMock
import json
import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from src.models.environment import EnvironmentModel
from src.views.environment import (
    EnvironmentView,
    EnvironmentCreated,
    EnvironmentRetrieved,
    EnvironmentSimulation,
)

from src.dependencies import get_environment_controller

from src import app

client = TestClient(app)


@pytest.fixture
def stub_environment_simulation_dump():
    env_simulation = EnvironmentSimulation()
    env_simulation_json = env_simulation.model_dump_json()
    return json.loads(env_simulation_json)


@pytest.fixture(autouse=True)
def mock_controller_instance():
    with patch("src.dependencies.EnvironmentController") as mock_class:
        mock_controller = AsyncMock()
        mock_controller.post_environment = AsyncMock()
        mock_controller.get_environment_by_id = AsyncMock()
        mock_controller.put_environment_by_id = AsyncMock()
        mock_controller.delete_environment_by_id = AsyncMock()
        mock_controller.get_environment_simulation = AsyncMock()
        mock_controller.get_rocketpy_environment_binary = AsyncMock()
        
        mock_class.return_value = mock_controller
        
        
        get_environment_controller.cache_clear()
        
        yield mock_controller
        
        get_environment_controller.cache_clear()


def test_create_environment(stub_environment_dump, mock_controller_instance):
    mock_response = AsyncMock(
        return_value=EnvironmentCreated(environment_id='123')
    )
    mock_controller_instance.post_environment = mock_response
    response = client.post('/environments/', json=stub_environment_dump)
    assert response.status_code == 201
    assert response.json() == {
        'environment_id': '123',
        'message': 'Environment successfully created',
    }
    mock_controller_instance.post_environment.assert_called_once_with(
        EnvironmentModel(**stub_environment_dump)
    )


def test_create_environment_optional_params(
    stub_environment_dump, mock_controller_instance
):
    stub_environment_dump.update(
        {
            'latitude': 0,
            'longitude': 0,
            'elevation': 1,
            'atmospheric_model_type': 'standard_atmosphere',
            'atmospheric_model_file': None,
            'date': '2021-01-01T00:00:00',
        }
    )
    mock_response = AsyncMock(
        return_value=EnvironmentCreated(environment_id='123')
    )
    mock_controller_instance.post_environment = mock_response
    response = client.post('/environments/', json=stub_environment_dump)
    assert response.status_code == 201
    assert response.json() == {
        'environment_id': '123',
        'message': 'Environment successfully created',
    }


def test_create_environment_invalid_input():
    response = client.post(
        '/environments/', json={'latitude': 'foo', 'longitude': 'bar'}
    )
    assert response.status_code == 422


def test_create_environment_server_error(
    stub_environment_dump, mock_controller_instance
):
    mock_response = AsyncMock(side_effect=HTTPException(status_code=500))
    mock_controller_instance.post_environment = mock_response
    response = client.post('/environments/', json=stub_environment_dump)
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}


def test_read_environment(stub_environment_dump, mock_controller_instance):
    environment_view = EnvironmentView(
        environment_id='123', **stub_environment_dump
    )
    mock_response = AsyncMock(
        return_value=EnvironmentRetrieved(environment=environment_view)
    )
    mock_controller_instance.get_environment_by_id = mock_response
    response = client.get('/environments/123')
    assert response.status_code == 200
    assert response.json() == {
        'message': 'Environment successfully retrieved',
        'environment': json.loads(environment_view.model_dump_json()),
    }
    mock_controller_instance.get_environment_by_id.assert_called_once_with(
        '123'
    )


def test_read_environment_not_found(mock_controller_instance):
    mock_response = AsyncMock(side_effect=HTTPException(status_code=404))
    mock_controller_instance.get_environment_by_id = mock_response
    response = client.get('/environments/123')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}
    mock_controller_instance.get_environment_by_id.assert_called_once_with(
        '123'
    )


def test_read_environment_server_error(mock_controller_instance):
    mock_response = AsyncMock(side_effect=HTTPException(status_code=500))
    mock_controller_instance.get_environment_by_id = mock_response
    response = client.get('/environments/123')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}


def test_update_environment(stub_environment_dump, mock_controller_instance):
    mock_reponse = AsyncMock(return_value=None)
    mock_controller_instance.put_environment_by_id = mock_reponse
    response = client.put('/environments/123', json=stub_environment_dump)
    assert response.status_code == 204
    mock_controller_instance.put_environment_by_id.assert_called_once_with(
        '123', EnvironmentModel(**stub_environment_dump)
    )


def test_update_environment_invalid_input():
    response = client.put(
        '/environments/123', json={'consignment': 'foo', 'delivery': 'bar'}
    )
    assert response.status_code == 422


def test_update_environment_not_found(
    stub_environment_dump, mock_controller_instance
):
    mock_reponse = AsyncMock(side_effect=HTTPException(status_code=404))
    mock_controller_instance.put_environment_by_id = mock_reponse
    response = client.put('/environments/123', json=stub_environment_dump)
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}
    mock_controller_instance.put_environment_by_id.assert_called_once_with(
        '123', EnvironmentModel(**stub_environment_dump)
    )


def test_update_environment_server_error(
    stub_environment_dump, mock_controller_instance
):
    mock_response = AsyncMock(side_effect=HTTPException(status_code=500))
    mock_controller_instance.put_environment_by_id = mock_response
    response = client.put('/environments/123', json=stub_environment_dump)
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}


def test_delete_environment(mock_controller_instance):
    mock_reponse = AsyncMock(return_value=None)
    mock_controller_instance.delete_environment_by_id = mock_reponse
    response = client.delete('/environments/123')
    assert response.status_code == 204
    mock_controller_instance.delete_environment_by_id.assert_called_once_with(
        '123'
    )


def test_delete_environment_server_error(mock_controller_instance):
    mock_response = AsyncMock(side_effect=HTTPException(status_code=500))
    mock_controller_instance.delete_environment_by_id = mock_response
    response = client.delete('/environments/123')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}


def test_get_environment_simulation_success(
    stub_environment_simulation_dump, mock_controller_instance
):
    mock_reponse = AsyncMock(
        return_value=EnvironmentSimulation(**stub_environment_simulation_dump)
    )
    mock_controller_instance.get_environment_simulation = mock_reponse
    response = client.get('/environments/123/simulate')
    assert response.status_code == 200
    assert response.json() == stub_environment_simulation_dump
    mock_controller_instance.get_environment_simulation.assert_called_once_with(
        '123'
    )


def test_get_environment_simulation_not_found(mock_controller_instance):
    mock_response = AsyncMock(side_effect=HTTPException(status_code=404))
    mock_controller_instance.get_environment_simulation = mock_response
    response = client.get('/environments/123/simulate')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}
    mock_controller_instance.get_environment_simulation.assert_called_once_with(
        '123'
    )


def test_get_environment_simulation_server_error(mock_controller_instance):
    mock_response = AsyncMock(side_effect=HTTPException(status_code=500))
    mock_controller_instance.get_environment_simulation = mock_response
    response = client.get('/environments/123/simulate')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}


def test_read_rocketpy_environment_binary(mock_controller_instance):
    mock_response = AsyncMock(return_value=b'rocketpy')
    mock_controller_instance.get_rocketpy_environment_binary = mock_response
    response = client.get('/environments/123/rocketpy')
    assert response.status_code == 200
    assert response.content == b'rocketpy'
    assert response.headers['content-type'] == 'application/octet-stream'
    mock_controller_instance.get_rocketpy_environment_binary.assert_called_once_with(
        '123'
    )


def test_read_rocketpy_environment_binary_not_found(mock_controller_instance):
    mock_response = AsyncMock(side_effect=HTTPException(status_code=404))
    mock_controller_instance.get_rocketpy_environment_binary = mock_response
    response = client.get('/environments/123/rocketpy')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}
    mock_controller_instance.get_rocketpy_environment_binary.assert_called_once_with(
        '123'
    )


def test_read_rocketpy_environment_binary_server_error(
    mock_controller_instance,
):
    mock_response = AsyncMock(side_effect=HTTPException(status_code=500))
    mock_controller_instance.get_rocketpy_environment_binary = mock_response
    response = client.get('/environments/123/rocketpy')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}
