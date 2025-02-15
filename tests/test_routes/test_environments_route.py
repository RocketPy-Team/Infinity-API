from unittest.mock import patch
import json
import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from lib.models.environment import EnvironmentModel
from lib.controllers.environment import EnvironmentController
from lib.views.environment import (
    EnvironmentCreated,
    EnvironmentUpdated,
    EnvironmentDeleted,
    EnvironmentSummary,
)
from lib import app

client = TestClient(app)


@pytest.fixture
def stub_environment_summary_dump():
    env_summary = EnvironmentSummary()
    env_summary_json = env_summary.model_dump_json()
    return json.loads(env_summary_json)

@pytest.fixture(autouse=True)
def mock_controller_instance():
    with patch(
        "lib.routes.environment.EnvironmentController", autospec=True
    ) as mock_controller:
        mock_controller_instance = mock_controller.return_value
        mock_controller_instance.post_environment = Mock()
        mock_controller_instance.get_environment_by_id = Mock()
        mock_controller_instance.put_environment_by_id = Mock()
        mock_controller_instance.delete_environment_by_id = Mock()
        yield mock_controller_instance

def test_create_environment(stub_environment_dump, mock_controller_instance):
    mock_response = AsyncMock(return_value=EnvironmentCreated(environment_id='123'))
    mock_controller_instance.post_environment = mock_response
    response = client.post('/environments/', json=stub_environment_dump)
    assert response.status_code == 200
    assert response.json() == {
        'environment_id': '123',
        'message': 'environment successfully created',
    }
    mock_controller_instance.post_environment.assert_called_once_with(
        EnvironmentModel(**stub_environment_dump)
    )

def test_create_environment_optional_params(stub_environment_dump, mock_controller_instance):
    stub_environment_dump.update({
        'latitude': 0,
        'longitude': 0,
        'elevation': 1,
        'atmospheric_model_type': 'STANDARD_ATMOSPHERE',
        'atmospheric_model_file': None,
        'date': '2021-01-01T00:00:00',
    })
    mock_response = AsyncMock(return_value=EnvironmentCreated(environment_id='123'))
    mock_controller_instance.post_environment = mock_response
    response = client.post('/environments/', json=stub_environment_dump)
    assert response.status_code == 200
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

def test_read_environment(stub_env):
    stub_environment_out = EnvironmentModelOut(environment_id='123', **stub_environment_dump)
    mock_response = AsyncMock(
        return_value=EnvironmentRetrieved(environment=stub_environment_out)
    )
    mock_controller_instance.get_environment_by_id = mock_response
    response = client.get('/environments/123')
    assert response.status_code == 200
    assert response.json() == {
        'message': 'Environment successfully retrieved',
        'environment': json.loads(stub_environment_out.model_dump_json()),
    }

def test_read_environment_not_found(mock_controller_instance):
    mock_response = AsyncMock(side_effect=HTTPException(status_code=404))
    mock_controller_instance.get_environment_by_id = mock_response
    response = client.get('/environments/123')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}
    mock_controller_instance.get_environment_by_id.assert_called_once_with('123')

def test_read_environment_server_error(mock_controller_instance):
    mock_response = AsyncMock(side_effect=HTTPException(status_code=500))
    mock_controller_instance.get_environment_by_id = mock_response
    response = client.get('/environments/123')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}

def test_update_environment(stub_environment_dump, mock_controller_instance):
    mock_reponse = AsyncMock(return_value=EnvironmentUpdated(environment_id='123'))
    mock_controller_instance.put_environment_by_id = mock_reponse
    response = client.put('/environments/123', json=stub_environment_dump)
    assert response.status_code == 200
    assert response.json() == {
        'message': 'Environment successfully updated',
    }
    mock_controller_instance.put_environment_by_id.assert_called_once_with(
        '123', EnvironmentModel(**stub_environment_dump)
    )

def test_update_environment_invalid_input():
    response = client.put(
        '/environments/123', json={'consignment': 'foo', 'delivery': 'bar'}
    )
    assert response.status_code == 422

def test_update_environment_not_found(stub_environment_dump, mock_controller_instance):
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
    mock_reponse = AsyncMock(return_value=EnvironmentDeleted(environment_id='123'))
    mock_controller_instance.delete_environment_by_id = mock_reponse
    response = client.delete('/environments/123')
    assert response.status_code == 200
    assert response.json() == {
        'message': 'Environment successfully deleted',
    }
    mock_controller_instance.delete_environment_by_id.assert_called_once_with('123')

def test_delete_environment_server_error(mock_controller_instance):
    mock_response = AsyncMock(side_effect=HTTPException(status_code=500))
    mock_controller_instance.delete_environment_by_id = mock_response
    response = client.delete('/environments/123')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}

def test_simulate_environment_success(
    stub_environment_summary_dump, mock_controller_instance
):
    mock_reponse = AsyncMock(return_value=EnvironmentSummary(**stub_environment_summary_dump))
    mock_controller_instance.get_environment_simulation = mock_reponse
    response = client.get('/environments/123/summary')
    assert response.status_code == 200
    assert response.json() == stub_environment_summary_dump
    mock_controller_instance.get_environment_simulation.assert_called_once_with('123')

def test_simulate_environment_not_found(mock_controller_instance):
    mock_response = AsyncMock(side_effect=HTTPException(status_code=404))
    mock_controller_instance.get_environment_simulation = mock_response
    response = client.get('/environments/123/summary')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}
    mock_controller_instance.get_environment_simulation.assert_called_once_with('123')

def test_simulate_environment_server_error(mock_controller_instance):
    mock_response = AsyncMock(side_effect=HTTPException(status_code=500))
    mock_controller_instance.get_environment_simulation = mock_response
    response = client.get('/environments/123/summary')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}

def test_read_rocketpy_environment(mock_controller_instance):
    mock_response = AsyncMock(return_value=b'rocketpy')
    mock_controller_instance.get_rocketpy_environment_binary = mock_response
    response = client.get('/environments/123/rocketpy')
    assert response.status_code == 203
    assert response.content == b'rocketpy'
    assert response.headers['content-type'] == 'application/octet-stream'
    mock_controller_instance.get_rocketpy_environment_binary.assert_called_once_with(
        '123'
    )

def test_read_rocketpy_environment_not_found(mock_controller_instance):
    mock_response = AsyncMock(side_effect=HTTPException(status_code=404))
    mock_controller_instance.get_rocketpy_environment_binary = mock_response
    response = client.get('/environments/123/rocketpy')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}
    mock_controller_instance.get_rocketpy_environment_binary.assert_called_once_with(
        '123'
    )

def test_read_rocketpy_environment_server_error(mock_controller_instance):
    mock_response = AsyncMock(side_effect=HTTPException(status_code=500))
    mock_controller_instance.get_rocketpy_environment_binary = mock_response
    response = client.get('/environments/123/rocketpy')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}
