from unittest.mock import patch, Mock, AsyncMock
import json
import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from lib.models.environment import EnvironmentModel
from lib.models.flight import FlightModel
from lib.models.motor import MotorModel, MotorKinds
from lib.models.rocket import RocketModel
from lib.views.motor import MotorView
from lib.views.rocket import RocketView
from lib.views.flight import (
    FlightCreated,
    FlightUpdated,
    FlightRetrieved,
    FlightDeleted,
    FlightSummary,
    FlightView,
)
from lib import app

client = TestClient(app)


@pytest.fixture
def stub_flight_dump(stub_environment_dump, stub_rocket_dump):
    flight = {
        'name': 'Test Flight',
        'environment': stub_environment_dump,
        'rocket': stub_rocket_dump,
        'rail_length': 1,
        'time_overshoot': True,
        'terminate_on_apogee': True,
        'equations_of_motion': 'standard',
    }
    return flight


@pytest.fixture
def stub_flight_summary_dump():
    flight_summary = FlightSummary()
    flight_summary_json = flight_summary.model_dump_json()
    return json.loads(flight_summary_json)


@pytest.fixture(autouse=True)
def mock_controller_instance():
    with patch(
        "lib.routes.flight.FlightController", autospec=True
    ) as mock_controller:
        mock_controller_instance = mock_controller.return_value
        mock_controller_instance.post_flight = Mock()
        mock_controller_instance.get_flight = Mock()
        mock_controller_instance.put_flight = Mock()
        mock_controller_instance.delete_flight_by_id = Mock()
        yield mock_controller_instance


def test_create_flight(stub_flight_dump, mock_controller_instance):
    mock_response = AsyncMock(return_value=FlightCreated(flight_id='123'))
    mock_controller_instance.post_flight = mock_response
    with patch.object(
            MotorModel, 'set_motor_kind', side_effect=None
    ) as mock_set_motor_kind:
        response = client.post('/flights/', json=stub_flight_dump, params={'motor_kind': 'HYBRID'})
        assert response.status_code == 200
        assert response.json() == {
            'flight_id': '123',
            'message': 'flight successfully created',
        }
        mock_set_motor_kind.assert_called_once_with(MotorKinds.HYBRID)
        mock_controller_instance.post_flight.assert_called_once_with(
            FlightModel(**stub_flight_dump))


def test_create_flight_optional_params(stub_flight_dump, mock_controller_instance):
    stub_flight_dump.update(
        {
            'inclination': 0,
            'heading': 0,
            'max_time': 1,
            'max_time_step': 1.0,
            'min_time_step': 1,
            'rtol': 1.0,
            'atol': 1.0,
            'verbose': True,
        }
    )
    mock_response = AsyncMock(return_value=FlightCreated(flight_id='123'))
    mock_controller_instance.post_flight = mock_response
    with patch.object(
            MotorModel, 'set_motor_kind', side_effect=None
    ) as mock_set_motor_kind:
        response = client.post('/flights/', json=stub_flight_dump, params={'motor_kind': 'HYBRID'})
        assert response.status_code == 200
        assert response.json() == {
            'flight_id': '123',
            'message': 'flight successfully created',
        }
        mock_set_motor_kind.assert_called_once_with(MotorKinds.HYBRID)
        mock_controller_instance.post_flight.assert_called_once_with(
            FlightModel(**stub_flight_dump))


def test_create_flight_invalid_input():
    response = client.post(
        '/flights/', json={'environment': 'foo', 'rocket': 'bar'}
    )
    assert response.status_code == 422


def test_create_flight_server_error(stub_flight_dump, mock_controller_instance):
    mock_response = AsyncMock(
        side_effect=HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    )
    mock_controller_instance.post_flight = mock_response
    response = client.post('/flights/', json=stub_flight_dump, params={'motor_kind': 'HYBRID'})
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}


def test_read_flight(stub_flight_dump, stub_rocket_dump, stub_motor_dump, mock_controller_instance):
    del stub_rocket_dump['motor']
    del stub_flight_dump['rocket']
    motor_view = MotorView(**stub_motor_dump, selected_motor_kind=MotorKinds.HYBRID.value)
    rocket_view = RocketView(**stub_rocket_dump, motor=motor_view)
    flight_view = FlightView(**stub_flight_dump, rocket=rocket_view)
    mock_response = AsyncMock(return_value=FlightRetrieved(flight=flight_view))
    mock_controller_instance.get_flight = mock_response
    response = client.get('/flights/123')
    assert response.status_code == 200
    assert response.json() == json.loads(flight_view.model_dump_json())
    mock_controller_instance.get_flight.assert_called_once_with('123')


def test_read_flight_not_found(mock_controller_instance):
    mock_controller_instance.get_flight.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND
    )
    response = client.get('/flights/123')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}


def test_read_flight_server_error(mock_controller_instance):
    mock_controller_instance.get_flight.side_effect = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    response = client.get('/flights/123')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}

def test_update_flight_by_id(stub_flight_dump, mock_controller_instance):
    mock_response = AsyncMock(return_value=FlightUpdated(flight_id='123'))
    mock_controller_instance.put_flight = mock_response
    with patch.object(
        MotorModel, 'set_motor_kind', side_effect=None
    ) as mock_set_motor_kind:
        response = client.put(
            '/flights/123',
            json=stub_flight_dump,
            params={'motor_kind': 'HYBRID'},
        )
        assert response.status_code == 200
        assert response.json() == {
            'flight_id': '123',
            'message': 'Flight successfully updated',
        }
        mock_set_motor_kind.assert_called_once_with(MotorKinds.HYBRID)
        mock_controller_instance.put_flight.assert_called_once_with(
            '123', FlightModel(**stub_flight_dump)
        )

def test_update_env_by_flight_id(stub_environment_dump, mock_controller_instance):
    mock_response = AsyncMock(return_value=FlightUpdated(flight_id='123'))
    mock_controller_instance.update_env_by_flight_id = mock_response
    response = client.put('/flights/123/env', json=stub_environment_dump)
    assert response.status_code == 200
    assert response.json() == {
        'flight_id': '123',
        'message': 'Flight successfully updated',
    }
    mock_controller_instance.update_env_by_flight_id.assert_called_once_with(
        '123', env=EnvironmentModel(**stub_environment_dump)
    )


def test_update_rocket_by_flight_id(stub_rocket_dump, mock_controller_instance):
    mock_response = AsyncMock(return_value=FlightUpdated(flight_id='123'))
    mock_controller_instance.update_rocket_by_flight_id = mock_response
    with patch.object(
        MotorModel, 'set_motor_kind', side_effect=None
    ) as mock_set_motor_kind:
        response = client.put(
            '/flights/123/rocket',
            json=stub_rocket_dump,
            params={'motor_kind': 'HYBRID'},
        )
        assert response.status_code == 200
        assert response.json() == {
            'flight_id': '123',
            'message': 'Flight successfully updated',
        }
        mock_set_motor_kind.assert_called_once_with(MotorKinds.HYBRID)
        mock_controller_instance.update_rocket_by_flight_id.assert_called_once_with(
            '123', RocketModel(**stub_rocket_dump)
        )


def test_update_env_by_flight_id_invalid_input():
    response = client.put('/flights/123', json={'environment': 'foo'})
    assert response.status_code == 422


def test_update_rocket_by_flight_id_invalid_input():
    response = client.put('/flights/123', json={'rocket': 'bar'})
    assert response.status_code == 422


def test_update_flight_invalid_input():
    response = client.put(
        '/flights/123',
        json={'environment': 'foo', 'rocket': 'bar'},
        params={'motor_kind': 'GENERIC'},
    )
    assert response.status_code == 422


def test_update_flight_not_found(stub_flight_dump, mock_controller_instance):
    mock_controller_instance.put_flight.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND
    )
    response = client.put(
        '/flights/123',
        json=stub_flight_dump,
        params={'motor_kind': 'HYBRID'},
    )
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}


def test_update_flight_server_error(stub_flight_dump, mock_controller_instance):
    mock_controller_instance.put_flight.side_effect = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    response = client.put(
        '/flights/123',
        json=stub_flight_dump,
        params={'motor_kind': 'HYBRID'},
    )
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}


def test_update_env_by_flight_id_not_found(stub_environment_dump, mock_controller_instance):
    mock_controller_instance.update_env_by_flight_id.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND
    )
    response = client.put('/flights/123/env', json=stub_environment_dump)
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}


def test_update_env_by_flight_id_server_error(stub_environment_dump, mock_controller_instance):
    mock_controller_instance.update_env_by_flight_id.side_effect = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    response = client.put('/flights/123/env', json=stub_environment_dump)
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}


def test_update_rocket_by_flight_id_not_found(stub_rocket_dump, mock_controller_instance):
    mock_controller_instance.update_rocket_by_flight_id.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND
    )
    response = client.put(
        '/flights/123/rocket',
        json=stub_rocket_dump,
        params={'motor_kind': 'HYBRID'},
    )
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}


def test_update_rocket_by_flight_id_server_error(stub_rocket_dump, mock_controller_instance):
    mock_controller_instance.update_rocket_by_flight_id.side_effect = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    response = client.put(
        '/flights/123/rocket',
        json=stub_rocket_dump,
        params={'motor_kind': 'HYBRID'},
    )
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}


def test_delete_flight(mock_controller_instance):
    mock_response = AsyncMock(return_value=FlightDeleted(flight_id='123'))
    mock_controller_instance.delete_flight_by_id = mock_response
    response = client.delete('/flights/123')
    assert response.status_code == 200
    assert response.json() == {
        'flight_id': '123',
        'message': 'Flight successfully deleted',
    }
    mock_controller_instance.delete_flight_by_id.assert_called_once_with('123')


def test_delete_flight_server_error(mock_controller_instance):
    mock_controller_instance.delete_flight_by_id.side_effect = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    response = client.delete('/flights/123')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}


def test_simulate_flight(stub_flight_summary_dump, mock_controller_instance):
    mock_response = AsyncMock(return_value=FlightSummary(**stub_flight_summary_dump))
    mock_controller_instance.simulate_flight = mock_response
    response = client.get('/flights/123/summary')
    assert response.status_code == 200
    assert response.json() == stub_flight_summary_dump
    mock_controller_instance.simulate_flight.assert_called_once_with('123')


def test_simulate_flight_not_found(mock_controller_instance):
    mock_controller_instance.simulate_flight.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND
    )
    response = client.get('/flights/123/summary')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}


def test_simulate_flight_server_error(mock_controller_instance):
    mock_controller_instance.simulate_flight.side_effect = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    response = client.get('/flights/123/summary')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}


def test_read_rocketpy_flight_binary(mock_controller_instance):
    mock_controller_instance.get_rocketpy_flight_binary = AsyncMock(return_value=b'rocketpy')
    response = client.get('/flights/123/rocketpy')
    assert response.status_code == 203
    assert response.content == b'rocketpy'
    assert response.headers['content-type'] == 'application/octet-stream'
    mock_controller_instance.get_rocketpy_flight_binary.assert_called_once_with('123')


def test_read_rocketpy_flight_binary_not_found(mock_controller_instance):
    mock_controller_instance.get_rocketpy_flight_binary.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND
    )
    response = client.get('/flights/123/rocketpy')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}


def test_read_rocketpy_flight_binary_server_error(mock_controller_instance):
    mock_controller_instance.get_rocketpy_flight_binary.side_effect = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    response = client.get('/flights/123/rocketpy')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}
