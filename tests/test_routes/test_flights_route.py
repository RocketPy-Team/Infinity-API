from unittest.mock import patch
import json
import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from lib.models.environment import EnvironmentModel
from lib.models.flight import FlightModel
from lib.models.motor import MotorModel, MotorKinds
from lib.models.rocket import RocketModel
from lib.controllers.flight import FlightController
from lib.views.motor import MotorView
from lib.views.rocket import RocketView
from lib.views.flight import (
    FlightCreated,
    FlightUpdated,
    FlightDeleted,
    FlightSummary,
    FlightView,
)
from lib import app

client = TestClient(app)


@pytest.fixture
def stub_flight(stub_environment_dump, stub_rocket_dump):
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
def stub_flight_summary():
    flight_summary = FlightSummary()
    flight_summary_json = flight_summary.model_dump_json()
    return json.loads(flight_summary_json)


def test_create_flight(stub_flight):
    with patch.object(
        FlightController,
        'create_flight',
        return_value=FlightCreated(flight_id='123'),
    ) as mock_create_flight:
        with patch.object(
            MotorModel, 'set_motor_kind', side_effect=None
        ) as mock_set_motor_kind:
            response = client.post(
                '/flights/', json=stub_flight, params={'motor_kind': 'HYBRID'}
            )
            assert response.status_code == 200
            assert response.json() == {
                'flight_id': '123',
                'message': 'Flight successfully created',
            }
            mock_set_motor_kind.assert_called_once_with(MotorKinds.HYBRID)
            mock_create_flight.assert_called_once_with(FlightModel(**stub_flight))


def test_create_flight_optional_params(stub_flight):
    stub_flight.update(
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
    with patch.object(
        FlightController,
        'create_flight',
        return_value=FlightCreated(flight_id='123'),
    ) as mock_create_flight:
        with patch.object(
            MotorModel, 'set_motor_kind', side_effect=None
        ) as mock_set_motor_kind:
            response = client.post(
                '/flights/', json=stub_flight, params={'motor_kind': 'HYBRID'}
            )
            assert response.status_code == 200
            assert response.json() == {
                'flight_id': '123',
                'message': 'Flight successfully created',
            }
            mock_set_motor_kind.assert_called_once_with(MotorKinds.HYBRID)
            mock_create_flight.assert_called_once_with(FlightModel(**stub_flight))


def test_create_flight_invalid_input():
    response = client.post(
        '/flights/', json={'environment': 'foo', 'rocket': 'bar'}
    )
    assert response.status_code == 422


def test_create_flight_server_error(stub_flight):
    with patch.object(
        FlightController,
        'create_flight',
        side_effect=HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    ):
        response = client.post(
            '/flights/', json=stub_flight, params={'motor_kind': 'HYBRID'}
        )
        assert response.status_code == 500
        assert response.json() == {'detail': 'Internal Server Error'}


def test_read_flight(stub_flight, stub_rocket_dump, stub_motor_dump):
    del stub_rocket_dump['motor']
    del stub_flight['rocket']
    motor_view = MotorView(**stub_motor_dump, selected_motor_kind=MotorKinds.HYBRID)
    rocket_view = RocketView(**stub_rocket_dump, motor=motor_view)
    flight_view = FlightView(**stub_flight, rocket=rocket_view)
    with patch.object(
        FlightController,
        'get_flight_by_id',
        return_value=flight_view,
    ) as mock_read_flight:
        response = client.get('/flights/123')
        assert response.status_code == 200
        assert response.json() == json.loads(flight_view.model_dump_json())
        mock_read_flight.assert_called_once_with('123')


def test_read_flight_not_found():
    with patch.object(
        FlightController,
        'get_flight_by_id',
        side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND),
    ) as mock_read_flight:
        response = client.get('/flights/123')
        assert response.status_code == 404
        assert response.json() == {'detail': 'Not Found'}
        mock_read_flight.assert_called_once_with('123')


def test_read_flight_server_error():
    with patch.object(
        FlightController,
        'get_flight_by_id',
        side_effect=HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    ):
        response = client.get('/flights/123')
        assert response.status_code == 500
        assert response.json() == {'detail': 'Internal Server Error'}


def test_update_flight(stub_flight):
    with patch.object(
        FlightController,
        'update_flight_by_id',
        return_value=FlightUpdated(flight_id='123'),
    ) as mock_update_flight:
        with patch.object(
            MotorModel, 'set_motor_kind', side_effect=None
        ) as mock_set_motor_kind:
            response = client.put(
                '/flights/123',
                json=stub_flight,
                params={'motor_kind': 'GENERIC'},
            )
            assert response.status_code == 200
            assert response.json() == {
                'flight_id': '123',
                'message': 'Flight successfully updated',
            }
            mock_update_flight.assert_called_once_with(
                '123', FlightModel(**stub_flight)
            )
            mock_set_motor_kind.assert_called_once_with(MotorKinds.GENERIC)


def test_update_env_by_flight_id(stub_environment_dump):
    with patch.object(
        FlightController,
        'update_env_by_flight_id',
        return_value=FlightUpdated(flight_id='123'),
    ) as mock_update_flight:
        response = client.put('/flights/123/env', json=stub_environment_dump)
        assert response.status_code == 200
        assert response.json() == {
            'flight_id': '123',
            'message': 'Flight successfully updated',
        }
        mock_update_flight.assert_called_once_with('123', env=EnvironmentModel(**stub_environment_dump))


def test_update_rocket_by_flight_id(stub_rocket_dump):
    with patch.object(
        FlightController,
        'update_rocket_by_flight_id',
        return_value=FlightUpdated(flight_id='123'),
    ) as mock_update_flight:
        response = client.put(
            '/flights/123/rocket',
            json=stub_rocket_dump,
            params={'motor_kind': 'GENERIC'},
        )
        assert response.status_code == 200
        assert response.json() == {
            'flight_id': '123',
            'message': 'Flight successfully updated',
        }
        assert mock_update_flight.call_count == 1
        assert mock_update_flight.call_args[0][0] == '123'
        assert mock_update_flight.call_args[1]['rocket'].model_dump() == RocketModel(**stub_rocket_dump).model_dump()


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


def test_update_flight_not_found(stub_flight):
    with patch.object(
        FlightController,
        'update_flight_by_id',
        side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND),
    ):
        response = client.put(
            '/flights/123', json=stub_flight, params={'motor_kind': 'HYBRID'}
        )
        assert response.status_code == 404
        assert response.json() == {'detail': 'Not Found'}


def test_update_flight_server_error(stub_flight):
    with patch.object(
        FlightController,
        'update_flight_by_id',
        side_effect=HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    ):
        response = client.put(
            '/flights/123', json=stub_flight, params={'motor_kind': 'HYBRID'}
        )
        assert response.status_code == 500
        assert response.json() == {'detail': 'Internal Server Error'}


def test_delete_flight():
    with patch.object(
        FlightController,
        'delete_flight_by_id',
        return_value=FlightDeleted(flight_id='123'),
    ) as mock_delete_flight:
        response = client.delete('/flights/123')
        assert response.status_code == 200
        assert response.json() == {
            'flight_id': '123',
            'message': 'Flight successfully deleted',
        }
        mock_delete_flight.assert_called_once_with('123')


def test_delete_flight_server_error():
    with patch.object(
        FlightController,
        'delete_flight_by_id',
        side_effect=HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    ):
        response = client.delete('/flights/123')
        assert response.status_code == 500
        assert response.json() == {'detail': 'Internal Server Error'}


def test_simulate_flight(stub_flight_summary):
    with patch.object(
        FlightController,
        'simulate_flight',
        return_value=FlightSummary(**stub_flight_summary),
    ) as mock_simulate_flight:
        response = client.get('/flights/123/summary')
        assert response.status_code == 200
        assert response.json() == stub_flight_summary
        mock_simulate_flight.assert_called_once_with('123')


def test_simulate_flight_not_found():
    with patch.object(
        FlightController,
        'simulate_flight',
        side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND),
    ) as mock_simulate_flight:
        response = client.get('/flights/123/summary')
        assert response.status_code == 404
        assert response.json() == {'detail': 'Not Found'}
        mock_simulate_flight.assert_called_once_with('123')


def test_simulate_flight_server_error():
    with patch.object(
        FlightController,
        'simulate_flight',
        side_effect=HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    ):
        response = client.get('/flights/123/summary')
        assert response.status_code == 500
        assert response.json() == {'detail': 'Internal Server Error'}


def test_read_rocketpy_flight():
    with patch.object(
        FlightController,
        'get_rocketpy_flight_binary',
        return_value=b'rocketpy',
    ) as mock_read_rocketpy_flight:
        response = client.get('/flights/123/rocketpy')
        assert response.status_code == 203
        assert response.content == b'rocketpy'
        assert response.headers['content-type'] == 'application/octet-stream'
        mock_read_rocketpy_flight.assert_called_once_with('123')


def test_read_rocketpy_flight_not_found():
    with patch.object(
        FlightController,
        'get_rocketpy_flight_binary',
        side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND),
    ) as mock_read_rocketpy_flight:
        response = client.get('/flights/123/rocketpy')
        assert response.status_code == 404
        assert response.json() == {'detail': 'Not Found'}
        mock_read_rocketpy_flight.assert_called_once_with('123')


def test_read_rocketpy_flight_server_error():
    with patch.object(
        FlightController,
        'get_rocketpy_flight_binary',
        side_effect=HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    ):
        response = client.get('/flights/123/rocketpy')
        assert response.status_code == 500
        assert response.json() == {'detail': 'Internal Server Error'}
