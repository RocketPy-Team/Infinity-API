from unittest.mock import patch
import json
import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from lib.models.motor import (
    MotorModel,
    MotorKinds,
)
from lib.controllers.motor import MotorController
from lib.views.motor import (
    MotorCreated,
    MotorUpdated,
    MotorDeleted,
    MotorSummary,
    MotorView,
)
from lib import app

client = TestClient(app)


@pytest.fixture
def stub_motor_dump_summary():
    motor_summary = MotorSummary()
    motor_summary_json = motor_summary.model_dump_json()
    return json.loads(motor_summary_json)

@pytest.fixture(autouse=True)
def mock_controller_instance():
    with patch(
        "lib.routes.motor.MotorController", autospec=True
    ) as mock_controller:
        mock_controller_instance = mock_controller.return_value
        mock_controller_instance.post_motor = Mock()
        mock_controller_instance.get_motor_by_id = Mock()
        mock_controller_instance.put_motor_by_id = Mock()
        mock_controller_instance.delete_motor_by_id = Mock()
        yield mock_controller_instance

def test_create_motor(stub_motor_dump, mock_controller_instance):
    mock_response = AsyncMock(return_value=MotorCreated(motor_id='123'))
    mock_controller_instance.post_motor = mock_response
    with patch.object(
            Motor, 'set_motor_kind', side_effect=None
        ) as mock_set_motor_kind:
        response = client.post('/motors/', json=stub_motor_dump, params={'motor_kind': 'HYBRID'})
        assert response.status_code == 200
        assert response.json() == {
            'motor_id': '123',
            'message': 'motor successfully created',
        }
        mock_set_motor_kind.assert_called_once_with(MotorKinds.HYBRID)
        mock_controller_instance.post_motor.assert_called_once_with(
            MotorModel(**stub_motor_dump))

def test_create_motor_optional_params(stub_motor_dump, mock_controller_instance):
    stub_motor_dump.update({
        'interpolation_method': 'linear',
        'coordinate_system_orientation': 'nozzle_to_combustion_chamber',
        'reshape_thrust_curve': False,
    })
    mock_response = AsyncMock(return_value=MotorCreated(motor_id='123'))
    mock_controller_instance.post_motor = mock_response
    with patch.object(
        Motor, 'set_motor_kind', side_effect=None
    ) as mock_set_motor_kind:
        response = client.post(
            '/motors/', json=stub_motor_dump, params={'motor_kind': 'HYBRID'}
        )
        assert response.status_code == 200
        assert response.json() == {
            'motor_id': '123',
            'message': 'motor successfully created',
        }
        mock_set_motor_kind.assert_called_once_with(MotorKinds.HYBRID)
        mock_controller_instance.post_motor.assert_called_once_with(MotorModel(**stub_motor_dump))

def test_create_generic_motor(stub_motor_dump, mock_controller_instance):
    stub_motor_dump.update(
        {
            'chamber_radius': 0,
            'chamber_height': 0,
            'chamber_position': 0,
            'propellant_initial_mass': 0,
            'nozzle_position': 0,
        }
    )
    mock_response = AsyncMock(return_value=MotorCreated(motor_id='123'))
    mock_controller_instance.post_motor = mock_response
    with patch.object(
        Motor, 'set_motor_kind', side_effect=None
    ) as mock_set_motor_kind:
        response = client.post(
            '/motors/', json=stub_motor_dump, params={'motor_kind': 'GENERIC'}
        )
        assert response.status_code == 200
        assert response.json() == {
            'motor_id': '123',
            'message': 'motor successfully created',
        }
        mock_set_motor_kind.assert_called_once_with(MotorKinds.GENERIC)
        mock_controller_instance.post_motor.assert_called_once_with(MotorModel(**stub_motor_dump))

def test_create_liquid_motor_level_tank(stub_motor_dump, stub_level_tank, mock_controller_instance):
    stub_motor_dump.update({'tanks': [stub_level_tank]})
    mock_response = AsyncMock(return_value=MotorCreated(motor_id='123'))
    mock_controller_instance.post_motor = mock_response
    with patch.object(
        Motor, 'set_motor_kind', side_effect=None
    ) as mock_set_motor_kind:
        response = client.post(
            '/motors/', json=stub_motor_dump, params={'motor_kind': 'LIQUID'}
        )
        assert response.status_code == 200
        assert response.json() == {
            'motor_id': '123',
            'message': 'motor successfully created',
        }
        mock_set_motor_kind.assert_called_once_with(MotorKinds.LIQUID)
        mock_controller_instance.post_motor.assert_called_once_with(MotorModel(**stub_motor_dump))

def test_create_liquid_motor_mass_flow_tank(stub_motor_dump, stub_mass_flow_tank, mock_controller_instance):
    stub_motor_dump.update({'tanks': [stub_mass_flow_tank]})
    mock_response = AsyncMock(return_value=MotorCreated(motor_id='123'))
    mock_controller_instance.post_motor = mock_response
    with patch.object(
        Motor, 'set_motor_kind', side_effect=None
    ) as mock_set_motor_kind:
        response = client.post(
            '/motors/', json=stub_motor_dump, params={'motor_kind': 'LIQUID'}
        )
        assert response.status_code == 200
        assert response.json() == {
            'motor_id': '123',
            'message': 'motor successfully created',
        }
        mock_set_motor_kind.assert_called_once_with(MotorKinds.LIQUID)
        mock_controller_instance.post_motor.assert_called_once_with(MotorModel(**stub_motor_dump))

def test_create_liquid_motor_ullage_tank(stub_motor_dump, stub_ullage_tank, mock_controller_instance):
    stub_motor_dump.update({'tanks': [stub_ullage_tank]})
    mock_response = AsyncMock(return_value=MotorCreated(motor_id='123'))
    mock_controller_instance.post_motor = mock_response
    with patch.object(
        Motor, 'set_motor_kind', side_effect=None
    ) as mock_set_motor_kind:
        response = client.post(
            '/motors/', json=stub_motor_dump, params={'motor_kind': 'LIQUID'}
        )
        assert response.status_code == 200
        assert response.json() == {
            'motor_id': '123',
            'message': 'motor successfully created',
        }
        mock_set_motor_kind.assert_called_once_with(MotorKinds.LIQUID)
        mock_controller_instance.post_motor.assert_called_once_with(MotorModel(**stub_motor_dump))

def test_create_liquid_motor_mass_tank(stub_motor_dump, stub_mass_tank, mock_controller_instance):
    stub_motor_dump.update({'tanks': [stub_mass_tank]})
    mock_response = AsyncMock(return_value=MotorCreated(motor_id='123'))
    mock_controller_instance.post_motor = mock_response
    with patch.object(
        Motor, 'set_motor_kind', side_effect=None
    ) as mock_set_motor_kind:
        response = client.post(
            '/motors/', json=stub_motor_dump, params={'motor_kind': 'LIQUID'}
        )
        assert response.status_code == 200
        assert response.json() == {
            'motor_id': '123',
            'message': 'motor successfully created',
        }
        mock_set_motor_kind.assert_called_once_with(MotorKinds.LIQUID)
        mock_controller_instance.post_motor.assert_called_once_with(MotorModel(**stub_motor_dump))

def test_create_hybrid_motor(stub_motor_dump, stub_level_tank, mock_controller_instance):
    stub_motor_dump.update(
        {
            'grain_number': 0,
            'grain_density': 0,
            'grain_outer_radius': 0,
            'grain_initial_inner_radius': 0,
            'grain_initial_height': 0,
            'grains_center_of_mass_position': 0,
            'grain_separation': 0,
            'throat_radius': 0,
            'tanks': [stub_level_tank],
        }
    )
    mock_response = AsyncMock(return_value=MotorCreated(motor_id='123'))
    mock_controller_instance.post_motor = mock_response
    with patch.object(
        Motor, 'set_motor_kind', side_effect=None
    ) as mock_set_motor_kind:
        response = client.post(
            '/motors/', json=stub_motor_dump, params={'motor_kind': 'HYBRID'}
        )
        assert response.status_code == 200
        assert response.json() == {
            'motor_id': '123',
            'message': 'motor successfully created',
        }
        mock_set_motor_kind.assert_called_once_with(MotorKinds.HYBRID)
        mock_controller_instance.post_motor.assert_called_once_with(MotorModel(**stub_motor_dump))

def test_create_solid_motor(stub_motor_dump, mock_controller_instance):
    stub_motor_dump.update(
        {
            'grain_number': 0,
            'grain_density': 0,
            'grain_outer_radius': 0,
            'grain_initial_inner_radius': 0,
            'grain_initial_height': 0,
            'grains_center_of_mass_position': 0,
            'grain_separation': 0,
        }
    )
    mock_response = AsyncMock(return_value=MotorCreated(motor_id='123'))
    mock_controller_instance.post_motor = mock_response
    with patch.object(
        Motor, 'set_motor_kind', side_effect=None
    ) as mock_set_motor_kind:
        response = client.post(
            '/motors/', json=stub_motor_dump, params={'motor_kind': 'SOLID'}
        )
        assert response.status_code == 200
        assert response.json() == {
            'motor_id': '123',
            'message': 'motor successfully created',
        }
        mock_set_motor_kind.assert_called_once_with(MotorKinds.SOLID)
        mock_controller_instance.post_motor.assert_called_once_with(MotorModel(**stub_motor_dump))

def test_create_motor_invalid_input():
    response = client.post(
        '/motors/', json={'burn_time': 'foo', 'nozzle_radius': 'bar'}
    )
    assert response.status_code == 422

def test_create_motor_server_error(stub_motor_dump, mock_controller_instance):
    mock_response = AsyncMock(side_effect=HTTPException(status_code=500))
    mock_controller_instance.post_motor = mock_response
    with patch.object(
        Motor, 'set_motor_kind', side_effect=None
    ) as mock_set_motor_kind:
        response = client.post('/motors/', json=stub_motor_dump, params={'motor_kind': 'HYBRID'})
        assert response.status_code == 500
        assert response.json() == {'detail': 'Internal Server Error'}
        mock_set_motor_kind.assert_called_once_with(MotorKinds.HYBRID)
        mock_controller_instance.post_motor.assert_called_once_with(MotorModel(**stub_motor_dump))

def test_read_motor(stub_motor_dump, mock_controller_instance):
    mock_response = AsyncMock(return_value=MotorView(**stub_motor_dump))
    mock_controller_instance.get_motor_by_id = mock_response
    response = client.get('/motors/123')
    assert response.status_code == 200
    assert response.json() == stub_motor_dump
    mock_controller_instance.get_motor_by_id.assert_called_once_with('123')

def test_read_motor_not_found(mock_controller_instance):
    mock_response = AsyncMock(side_effect=HTTPException(status_code=404))
    mock_controller_instance.get_motor_by_id = mock_response
    response = client.get('/motors/123')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}
    mock_controller_instance.get_motor_by_id.assert_called_once_with('123')

def test_read_motor_server_error(mock_controller_instance):
    mock_response = AsyncMock(side_effect=HTTPException(status_code=500))
    mock_controller_instance.get_motor_by_id = mock_response
    response = client.get('/motors/123')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}

def test_update_motor(stub_motor_dump, mock_controller_instance):
    mock_response = AsyncMock(return_value=MotorUpdated(motor_id='123'))
    mock_controller_instance.put_motor_by_id = mock_response
    with patch.object(
        Motor, 'set_motor_kind', side_effect=None
    ) as mock_set_motor_kind:
        response = client.put(
            '/motors/123', json=stub_motor_dump, params={'motor_kind': 'HYBRID'}
        )
        assert response.status_code == 200
        assert response.json() == {
            'motor_id': '123',
            'message': 'motor successfully updated',
        }
        mock_set_motor_kind.assert_called_once_with(MotorKinds.HYBRID)
        mock_controller_instance.put_motor_by_id.assert_called_once_with(
            '123', MotorModel(**stub_motor_dump)
        )

def test_update_motor_invalid_input():
    response = client.put(
        '/motors/123',
        json={'burn_time': 'foo', 'nozzle_radius': 'bar'},
        params={'motor_kind': 'HYBRID'},
    )
    assert response.status_code == 422

def test_update_motor_not_found(stub_motor_dump, mock_controller_instance):
    mock_response = AsyncMock(side_effect=HTTPException(status_code=404))
    mock_controller_instance.put_motor_by_id = mock_response
    with patch.object(
        Motor, 'set_motor_kind', side_effect=None
    ) as mock_set_motor_kind:
        response = client.put(
            '/motors/123', json=stub_motor_dump, params={'motor_kind': 'HYBRID'}
        )
        assert response.status_code == 404
        assert response.json() == {'detail': 'Not Found'}
        mock_set_motor_kind.assert_called_once_with(MotorKinds.HYBRID)
        mock_controller_instance.put_motor_by_id.assert_called_once_with(
            '123', MotorModel(**stub_motor_dump)
        )

def test_update_motor_server_error(stub_motor_dump, mock_controller_instance):
    mock_response = AsyncMock(side_effect=HTTPException(status_code=500))
    mock_controller_instance.put_motor_by_id = mock_response
    with patch.object(
        Motor, 'set_motor_kind', side_effect=None
    ) as mock_set_motor_kind:
        response = client.put(
            '/motors/123', json=stub_motor_dump, params={'motor_kind': 'HYBRID'}
        )
        assert response.status_code == 500
        assert response.json() == {'detail': 'Internal Server Error'}
        mock_set_motor_kind.assert_called_once_with(MotorKinds.HYBRID)
        mock_controller_instance.put_motor_by_id.assert_called_once_with(
            '123', MotorModel(**stub_motor_dump)
        )

def test_delete_motor(mock_controller_instance):
    mock_response = AsyncMock(return_value=MotorDeleted(motor_id='123'))
    mock_controller_instance.delete_motor_by_id = mock_response
    response = client.delete('/motors/123')
    assert response.status_code == 200
    assert response.json() == {
        'motor_id': '123',
        'message': 'motor successfully deleted',
    }
    mock_controller_instance.delete_motor_by_id.assert_called_once_with('123')

def test_delete_motor_server_error(mock_controller_instance):
    mock_response = AsyncMock(side_effect=HTTPException(status_code=500))
    mock_controller_instance.delete_motor_by_id = mock_response
    response = client.delete('/motors/123')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}
    mock_controller_instance.delete_motor_by_id.assert_called_once_with('123')


def test_simulate_motor(mock_controller_instance, stub_motor_dump_summary):
    mock_response = AsyncMock(return_value=MotorSummary(**stub_motor_dump_summary))
    mock_controller_instance.simulate_motor = mock_response
    response = client.get('/motors/123/summary')
    assert response.status_code == 200
    assert response.json() == stub_motor_dump_summary
    mock_controller_instance.simulate_motor.assert_called_once_with('123')


def test_simulate_motor_not_found(mock_controller_instance):
    mock_response = AsyncMock(side_effect=HTTPException(status_code=404))
    mock_controller_instance.simulate_motor = mock_response
    response = client.get('/motors/123/summary')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}
    mock_controller_instance.simulate_motor.assert_called_once_with('123')

def test_simulate_motor_server_error(mock_controller_instance):
    mock_response = AsyncMock(side_effect=HTTPException(status_code=500))
    mock_controller_instance.simulate_motor = mock_response
    response = client.get('/motors/123/summary')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}
    mock_controller_instance.simulate_motor.assert_called_once_with('123')

def test_read_rocketpy_motor(mock_controller_instance):
    mock_response = AsyncMock(return_value=b'rocketpy')
    mock_controller_instance.get_rocketpy_motor_binary = mock_response
    response = client.get('/motors/123/rocketpy')
    assert response.status_code == 203
    assert response.content == b'rocketpy'
    assert response.headers['content-type'] == 'application/octet-stream'
    mock_controller_instance.get_rocketpy_motor_binary.assert_called_once_with('123')

def test_read_rocketpy_motor_not_found(mock_controller_instance):
    mock_response = AsyncMock(side_effect=HTTPException(status_code=404))
    mock_controller_instance.get_rocketpy_motor_binary = mock_response
    response = client.get('/motors/123/rocketpy')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}
    mock_controller_instance.get_rocketpy_motor_binary.assert_called_once_with('123')

def test_read_rocketpy_motor_server_error(mock_controller_instance):
    mock_response = AsyncMock(side_effect=HTTPException(status_code=500))
    mock_controller_instance.get_rocketpy_motor_binary = mock_response
    response = client.get('/motors/123/rocketpy')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}
    mock_controller_instance.get_rocketpy_motor_binary.assert_called_once_with('123')
