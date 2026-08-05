from unittest.mock import patch, AsyncMock
import copy
import json
import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from src.models.environment import EnvironmentModel
from src.models.flight import FlightModel, FlightWithReferencesRequest
from src.models.rocket import RocketModel
from src.views.motor import MotorView
from src.views.rocket import RocketView
from src.views.flight import (
    FlightCreated,
    FlightImported,
    FlightRetrieved,
    FlightSimulation,
    FlightView,
)

from src.dependencies import get_flight_controller

from src import app

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
def stub_flight_simulate_dump():
    flight_simulate = FlightSimulation()
    flight_simulate_json = flight_simulate.model_dump_json()
    return json.loads(flight_simulate_json)


@pytest.fixture(autouse=True)
def mock_controller_instance():
    with patch("src.dependencies.FlightController") as mock_class:
        mock_controller = AsyncMock()
        mock_controller.post_flight = AsyncMock()
        mock_controller.get_flight_by_id = AsyncMock()
        mock_controller.put_flight_by_id = AsyncMock()
        mock_controller.delete_flight_by_id = AsyncMock()
        mock_controller.get_flight_simulation = AsyncMock()
        mock_controller.get_rocketpy_flight_rpy = AsyncMock()
        mock_controller.import_flight_from_rpy = AsyncMock()
        mock_controller.get_flight_notebook = AsyncMock()
        mock_controller.get_flight_kml = AsyncMock()
        mock_controller.update_environment_by_flight_id = AsyncMock()
        mock_controller.update_rocket_by_flight_id = AsyncMock()
        mock_controller.create_flight_from_references = AsyncMock()
        mock_controller.update_flight_from_references = AsyncMock()

        mock_class.return_value = mock_controller

        get_flight_controller.cache_clear()

        yield mock_controller

        get_flight_controller.cache_clear()


@pytest.fixture
def stub_flight_reference_payload(stub_flight_dump):
    partial_flight = copy.deepcopy(stub_flight_dump)
    partial_flight.pop('environment', None)
    partial_flight.pop('rocket', None)
    return {
        'environment_id': 'env-123',
        'rocket_id': 'rocket-456',
        'flight': partial_flight,
    }


def test_create_flight(stub_flight_dump, mock_controller_instance):
    mock_response = AsyncMock(return_value=FlightCreated(flight_id='123'))
    mock_controller_instance.post_flight = mock_response
    response = client.post('/flights/', json=stub_flight_dump)
    assert response.status_code == 201
    assert response.json() == {
        'flight_id': '123',
        'message': 'Flight successfully created',
    }
    mock_controller_instance.post_flight.assert_called_once_with(
        FlightModel(**stub_flight_dump)
    )


def test_create_flight_with_string_nested_fields(
    stub_flight_dump, mock_controller_instance
):
    payload = copy.deepcopy(stub_flight_dump)
    payload['environment'] = json.dumps(payload['environment'])
    payload['rocket'] = json.dumps(payload['rocket'])
    mock_controller_instance.post_flight = AsyncMock(
        return_value=FlightCreated(flight_id='123')
    )
    response = client.post('/flights/', json=payload)
    assert response.status_code == 201
    mock_controller_instance.post_flight.assert_called_once_with(
        FlightModel(**payload)
    )


def test_create_flight_from_references(
    stub_flight_reference_payload, mock_controller_instance
):
    mock_response = AsyncMock(return_value=FlightCreated(flight_id='123'))
    mock_controller_instance.create_flight_from_references = mock_response
    response = client.post(
        '/flights/from-references', json=stub_flight_reference_payload
    )
    assert response.status_code == 201
    assert response.json() == {
        'flight_id': '123',
        'message': 'Flight successfully created',
    }
    mock_controller_instance.create_flight_from_references.assert_called_once_with(
        FlightWithReferencesRequest(**stub_flight_reference_payload)
    )


def test_create_flight_from_references_with_string_payload(
    stub_flight_reference_payload, mock_controller_instance
):
    payload = copy.deepcopy(stub_flight_reference_payload)
    payload['flight'] = json.dumps(payload['flight'])
    mock_controller_instance.create_flight_from_references = AsyncMock(
        return_value=FlightCreated(flight_id='123')
    )
    response = client.post('/flights/from-references', json=payload)
    assert response.status_code == 201
    mock_controller_instance.create_flight_from_references.assert_called_once_with(
        FlightWithReferencesRequest(**payload)
    )


def test_create_flight_from_references_not_found(
    stub_flight_reference_payload, mock_controller_instance
):
    mock_controller_instance.create_flight_from_references.side_effect = (
        HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    )
    response = client.post(
        '/flights/from-references', json=stub_flight_reference_payload
    )
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}


def test_create_flight_from_references_server_error(
    stub_flight_reference_payload, mock_controller_instance
):
    mock_controller_instance.create_flight_from_references.side_effect = (
        HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    )
    response = client.post(
        '/flights/from-references', json=stub_flight_reference_payload
    )
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}


def test_create_flight_optional_params(
    stub_flight_dump, mock_controller_instance
):
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
    response = client.post('/flights/', json=stub_flight_dump)
    assert response.status_code == 201
    assert response.json() == {
        'flight_id': '123',
        'message': 'Flight successfully created',
    }
    mock_controller_instance.post_flight.assert_called_once_with(
        FlightModel(**stub_flight_dump)
    )


def test_create_flight_invalid_input():
    response = client.post(
        '/flights/', json={'environment': 'foo', 'rocket': 'bar'}
    )
    assert response.status_code == 422


def test_create_flight_server_error(
    stub_flight_dump, mock_controller_instance
):
    mock_response = AsyncMock(
        side_effect=HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    )
    mock_controller_instance.post_flight = mock_response
    response = client.post('/flights/', json=stub_flight_dump)
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}


def test_read_flight(
    stub_flight_dump,
    stub_rocket_dump,
    stub_motor_dump,
    mock_controller_instance,
):
    del stub_rocket_dump['motor']
    del stub_flight_dump['rocket']
    stub_motor_dump.update({'motor_kind': 'SOLID'})
    motor_view = MotorView(**stub_motor_dump)
    rocket_view = RocketView(**stub_rocket_dump, motor=motor_view)
    flight_view = FlightView(
        **stub_flight_dump, flight_id='123', rocket=rocket_view
    )
    mock_response = AsyncMock(return_value=FlightRetrieved(flight=flight_view))
    mock_controller_instance.get_flight_by_id = mock_response
    response = client.get('/flights/123')
    assert response.status_code == 200
    assert response.json() == {
        'message': 'Flight successfully retrieved',
        'flight': json.loads(flight_view.model_dump_json()),
    }
    mock_controller_instance.get_flight_by_id.assert_called_once_with('123')


def test_read_flight_not_found(mock_controller_instance):
    mock_controller_instance.get_flight_by_id.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND
    )
    response = client.get('/flights/123')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}


def test_read_flight_server_error(mock_controller_instance):
    mock_controller_instance.get_flight_by_id.side_effect = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    response = client.get('/flights/123')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}


def test_update_flight_by_id(stub_flight_dump, mock_controller_instance):
    mock_response = AsyncMock(return_value=None)
    mock_controller_instance.put_flight_by_id = mock_response
    response = client.put('/flights/123', json=stub_flight_dump)
    assert response.status_code == 204
    mock_controller_instance.put_flight_by_id.assert_called_once_with(
        '123', FlightModel(**stub_flight_dump)
    )


def test_update_flight_with_string_nested_fields(
    stub_flight_dump, mock_controller_instance
):
    payload = copy.deepcopy(stub_flight_dump)
    payload['environment'] = json.dumps(payload['environment'])
    payload['rocket'] = json.dumps(payload['rocket'])
    mock_controller_instance.put_flight_by_id = AsyncMock(return_value=None)
    response = client.put('/flights/123', json=payload)
    assert response.status_code == 204
    mock_controller_instance.put_flight_by_id.assert_called_once_with(
        '123', FlightModel(**payload)
    )


def test_update_flight_from_references(
    stub_flight_reference_payload, mock_controller_instance
):
    mock_response = AsyncMock(return_value=None)
    mock_controller_instance.update_flight_from_references = mock_response
    response = client.put(
        '/flights/123/from-references',
        json=stub_flight_reference_payload,
    )
    assert response.status_code == 204
    mock_controller_instance.update_flight_from_references.assert_called_once_with(
        '123', FlightWithReferencesRequest(**stub_flight_reference_payload)
    )


def test_update_flight_from_references_with_string_payload(
    stub_flight_reference_payload, mock_controller_instance
):
    payload = copy.deepcopy(stub_flight_reference_payload)
    payload['flight'] = json.dumps(payload['flight'])
    mock_controller_instance.update_flight_from_references = AsyncMock(
        return_value=None
    )
    response = client.put('/flights/123/from-references', json=payload)
    assert response.status_code == 204
    mock_controller_instance.update_flight_from_references.assert_called_once_with(
        '123', FlightWithReferencesRequest(**payload)
    )


def test_update_flight_from_references_not_found(
    stub_flight_reference_payload, mock_controller_instance
):
    mock_controller_instance.update_flight_from_references.side_effect = (
        HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    )
    response = client.put(
        '/flights/123/from-references',
        json=stub_flight_reference_payload,
    )
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}


def test_update_flight_from_references_server_error(
    stub_flight_reference_payload, mock_controller_instance
):
    mock_controller_instance.update_flight_from_references.side_effect = (
        HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    )
    response = client.put(
        '/flights/123/from-references',
        json=stub_flight_reference_payload,
    )
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}


def test_update_environment_by_flight_id(
    stub_environment_dump, mock_controller_instance
):
    mock_response = AsyncMock(return_value=None)
    mock_controller_instance.update_environment_by_flight_id = mock_response
    response = client.put(
        '/flights/123/environment', json=stub_environment_dump
    )
    assert response.status_code == 204
    mock_controller_instance.update_environment_by_flight_id.assert_called_once_with(
        '123', environment=EnvironmentModel(**stub_environment_dump)
    )


def test_update_rocket_by_flight_id(
    stub_rocket_dump, mock_controller_instance
):
    mock_response = AsyncMock(return_value=None)
    mock_controller_instance.update_rocket_by_flight_id = mock_response
    response = client.put('/flights/123/rocket', json=stub_rocket_dump)
    assert response.status_code == 204
    mock_controller_instance.update_rocket_by_flight_id.assert_called_once_with(
        '123', rocket=RocketModel(**stub_rocket_dump)
    )


def test_update_environment_by_flight_id_invalid_input():
    response = client.put('/flights/123', json={'environment': 'foo'})
    assert response.status_code == 422


def test_update_rocket_by_flight_id_invalid_input():
    response = client.put('/flights/123', json={'rocket': 'bar'})
    assert response.status_code == 422


def test_update_flight_invalid_input():
    response = client.put(
        '/flights/123', json={'environment': 'foo', 'rocket': 'bar'}
    )
    assert response.status_code == 422


def test_update_flight_not_found(stub_flight_dump, mock_controller_instance):
    mock_controller_instance.put_flight_by_id.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND
    )
    response = client.put('/flights/123', json=stub_flight_dump)
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}


def test_update_flight_server_error(
    stub_flight_dump, mock_controller_instance
):
    mock_controller_instance.put_flight_by_id.side_effect = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    response = client.put('/flights/123', json=stub_flight_dump)
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}


def test_update_environment_by_flight_id_not_found(
    stub_environment_dump, mock_controller_instance
):
    mock_controller_instance.update_environment_by_flight_id.side_effect = (
        HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    )
    response = client.put(
        '/flights/123/environment', json=stub_environment_dump
    )
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}


def test_update_environment_by_flight_id_server_error(
    stub_environment_dump, mock_controller_instance
):
    mock_controller_instance.update_environment_by_flight_id.side_effect = (
        HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    )
    response = client.put(
        '/flights/123/environment', json=stub_environment_dump
    )
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}


def test_update_rocket_by_flight_id_not_found(
    stub_rocket_dump, mock_controller_instance
):
    mock_controller_instance.update_rocket_by_flight_id.side_effect = (
        HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    )
    response = client.put('/flights/123/rocket', json=stub_rocket_dump)
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}


def test_update_rocket_by_flight_id_server_error(
    stub_rocket_dump, mock_controller_instance
):
    mock_controller_instance.update_rocket_by_flight_id.side_effect = (
        HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    )
    response = client.put('/flights/123/rocket', json=stub_rocket_dump)
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}


def test_delete_flight(mock_controller_instance):
    mock_response = AsyncMock(return_value=None)
    mock_controller_instance.delete_flight_by_id = mock_response
    response = client.delete('/flights/123')
    assert response.status_code == 204
    mock_controller_instance.delete_flight_by_id.assert_called_once_with('123')


def test_delete_flight_server_error(mock_controller_instance):
    mock_controller_instance.delete_flight_by_id.side_effect = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    response = client.delete('/flights/123')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}


def test_get_flight_simulation(
    stub_flight_simulate_dump, mock_controller_instance
):
    mock_response = AsyncMock(
        return_value=FlightSimulation(**stub_flight_simulate_dump)
    )
    mock_controller_instance.get_flight_simulation = mock_response
    response = client.get('/flights/123/simulate')
    assert response.status_code == 200
    assert response.json() == stub_flight_simulate_dump
    mock_controller_instance.get_flight_simulation.assert_called_once_with(
        '123'
    )


def test_get_flight_simulation_not_found(mock_controller_instance):
    mock_controller_instance.get_flight_simulation.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND
    )
    response = client.get('/flights/123/simulate')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}


def test_get_flight_simulation_server_error(mock_controller_instance):
    mock_controller_instance.get_flight_simulation.side_effect = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    response = client.get('/flights/123/simulate')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}


def test_read_rocketpy_flight_rpy(mock_controller_instance):
    mock_controller_instance.get_rocketpy_flight_rpy = AsyncMock(
        return_value=b'{"simulation": {}}',
    )
    response = client.get('/flights/123/rocketpy')
    assert response.status_code == 200
    assert response.content == b'{"simulation": {}}'
    assert response.headers['content-type'] == 'application/json'
    assert '.rpy' in response.headers['content-disposition']
    mock_controller_instance.get_rocketpy_flight_rpy.assert_called_once_with(
        '123'
    )


def test_read_rocketpy_flight_rpy_not_found(mock_controller_instance):
    mock_controller_instance.get_rocketpy_flight_rpy.side_effect = (
        HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    )
    response = client.get('/flights/123/rocketpy')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}


def test_read_rocketpy_flight_rpy_server_error(mock_controller_instance):
    mock_controller_instance.get_rocketpy_flight_rpy.side_effect = (
        HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    )
    response = client.get('/flights/123/rocketpy')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}


def test_read_flight_kml(mock_controller_instance):
    kml_bytes = b'<?xml version="1.0" encoding="UTF-8"?><kml></kml>'
    mock_controller_instance.get_flight_kml = AsyncMock(return_value=kml_bytes)
    response = client.get('/flights/123/kml')
    assert response.status_code == 200
    assert response.content == kml_bytes
    assert (
        response.headers['content-type']
        == 'application/vnd.google-earth.kml+xml'
    )
    assert 'flight_123.kml' in response.headers['content-disposition']
    mock_controller_instance.get_flight_kml.assert_called_once_with('123')


def test_read_flight_kml_not_found(mock_controller_instance):
    mock_controller_instance.get_flight_kml.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND
    )
    response = client.get('/flights/123/kml')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}


def test_read_flight_kml_server_error(mock_controller_instance):
    mock_controller_instance.get_flight_kml.side_effect = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    response = client.get('/flights/123/kml')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}


# --- Issue #56: Import flight from .rpy ---


def test_import_flight_from_rpy(mock_controller_instance):
    mock_controller_instance.import_flight_from_rpy = AsyncMock(
        return_value=FlightImported(
            flight_id='f1',
            rocket_id='r1',
            motor_id='m1',
            environment_id='e1',
        )
    )
    rpy_content = b'{"simulation": {}}'
    response = client.post(
        '/flights/upload',
        files={
            'file': (
                'flight.rpy',
                rpy_content,
                'application/json',
            )
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body['flight_id'] == 'f1'
    assert body['rocket_id'] == 'r1'
    assert body['motor_id'] == 'm1'
    assert body['environment_id'] == 'e1'
    assert body['message'] == "Flight successfully imported from .rpy file"
    mock_controller_instance.import_flight_from_rpy.assert_called_once_with(
        rpy_content
    )


def test_import_flight_from_rpy_invalid(mock_controller_instance):
    mock_controller_instance.import_flight_from_rpy.side_effect = (
        HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Invalid .rpy file: bad data',
        )
    )
    response = client.post(
        '/flights/upload',
        files={'file': ('bad.rpy', b'bad', 'application/json')},
    )
    assert response.status_code == 422


def test_import_flight_from_rpy_server_error(
    mock_controller_instance,
):
    mock_controller_instance.import_flight_from_rpy.side_effect = (
        HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    )
    response = client.post(
        '/flights/upload',
        files={'file': ('f.rpy', b'{}', 'application/json')},
    )
    assert response.status_code == 500


def test_import_flight_from_rpy_payload_too_large(
    mock_controller_instance,
):
    oversized = b"a" * (10 * 1024 * 1024 + 1)
    response = client.post(
        '/flights/upload',
        files={'file': ('large.rpy', oversized, 'application/json')},
    )
    assert response.status_code == 413
    assert response.json() == {
        'detail': 'Uploaded .rpy file exceeds 10 MB limit.'
    }
    mock_controller_instance.import_flight_from_rpy.assert_not_called()


# --- Issue #57: Export flight as notebook ---


def test_get_flight_notebook(mock_controller_instance):
    notebook = {
        'nbformat': 4,
        'nbformat_minor': 5,
        'metadata': {},
        'cells': [],
    }
    mock_controller_instance.get_flight_notebook = AsyncMock(
        return_value=notebook
    )
    response = client.get('/flights/123/notebook')
    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/x-ipynb+json'
    assert 'flight_123.ipynb' in response.headers['content-disposition']
    body = json.loads(response.content)
    assert body['nbformat'] == 4
    mock_controller_instance.get_flight_notebook.assert_called_once_with('123')


def test_get_flight_notebook_not_found(mock_controller_instance):
    mock_controller_instance.get_flight_notebook.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND
    )
    response = client.get('/flights/999/notebook')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}


def test_get_flight_notebook_server_error(mock_controller_instance):
    mock_controller_instance.get_flight_notebook.side_effect = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    response = client.get('/flights/123/notebook')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}
