from unittest.mock import patch
import json
import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from lib.models.motor import (
    Motor,
    MotorKinds,
    MotorTank,
    TankFluids,
    TankKinds,
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
def stub_motor():
    motor = Motor(
        thrust_source=[[0, 0]],
        burn_time=0,
        nozzle_radius=0,
        dry_mass=0,
        dry_inertia=[0, 0, 0],
        center_of_dry_mass_position=0,
    )
    motor_json = motor.model_dump_json()
    return json.loads(motor_json)


@pytest.fixture
def stub_tank():
    tank = MotorTank(
        geometry=[[(0, 0), 0]],
        gas=TankFluids(name='gas', density=0),
        liquid=TankFluids(name='liquid', density=0),
        flux_time=(0, 0),
        position=0,
        discretize=0,
        name='tank',
    )
    tank_json = tank.model_dump_json()
    return json.loads(tank_json)


@pytest.fixture
def stub_level_tank(stub_tank):
    stub_tank.update({'tank_kind': TankKinds.LEVEL, 'liquid_height': 0})
    return stub_tank


@pytest.fixture
def stub_mass_flow_tank(stub_tank):
    stub_tank.update(
        {
            'tank_kind': TankKinds.MASS_FLOW,
            'gas_mass_flow_rate_in': 0,
            'gas_mass_flow_rate_out': 0,
            'liquid_mass_flow_rate_in': 0,
            'liquid_mass_flow_rate_out': 0,
            'initial_liquid_mass': 0,
            'initial_gas_mass': 0,
        }
    )
    return stub_tank


@pytest.fixture
def stub_ullage_tank(stub_tank):
    stub_tank.update({'tank_kind': TankKinds.ULLAGE, 'ullage': 0})
    return stub_tank


@pytest.fixture
def stub_mass_tank(stub_tank):
    stub_tank.update(
        {'tank_kind': TankKinds.MASS, 'liquid_mass': 0, 'gas_mass': 0}
    )
    return stub_tank


@pytest.fixture
def stub_motor_summary():
    motor_summary = MotorSummary()
    motor_summary_json = motor_summary.model_dump_json()
    return json.loads(motor_summary_json)


def test_create_motor(stub_motor):
    with patch.object(
        MotorController,
        'create_motor',
        return_value=MotorCreated(motor_id='123'),
    ) as mock_create_motor:
        with patch.object(
            Motor, 'set_motor_kind', side_effect=None
        ) as mock_set_motor_kind:
            response = client.post(
                '/motors/', json=stub_motor, params={'motor_kind': 'HYBRID'}
            )
            assert response.status_code == 200
            assert response.json() == {
                'motor_id': '123',
                'message': 'Motor successfully created',
            }
            mock_set_motor_kind.assert_called_once_with(MotorKinds.HYBRID)
            mock_create_motor.assert_called_once_with(Motor(**stub_motor))


def test_create_motor_optional_params(stub_motor):
    stub_motor.update(
        {
            'interpolation_method': 'LINEAR',
            'coordinate_system_orientation': 'NOZZLE_TO_COMBUSTION_CHAMBER',
            'reshape_thrust_curve': False,
        }
    )
    with patch.object(
        MotorController,
        'create_motor',
        return_value=MotorCreated(motor_id='123'),
    ) as mock_create_motor:
        with patch.object(
            Motor, 'set_motor_kind', side_effect=None
        ) as mock_set_motor_kind:
            response = client.post(
                '/motors/', json=stub_motor, params={'motor_kind': 'HYBRID'}
            )
            assert response.status_code == 200
            assert response.json() == {
                'motor_id': '123',
                'message': 'Motor successfully created',
            }
            mock_set_motor_kind.assert_called_once_with(MotorKinds.HYBRID)
            mock_create_motor.assert_called_once_with(Motor(**stub_motor))


def test_create_generic_motor(stub_motor):
    stub_motor.update(
        {
            'chamber_radius': 0,
            'chamber_height': 0,
            'chamber_position': 0,
            'propellant_initial_mass': 0,
            'nozzle_position': 0,
        }
    )
    with patch.object(
        MotorController,
        'create_motor',
        return_value=MotorCreated(motor_id='123'),
    ) as mock_create_motor:
        with patch.object(
            Motor, 'set_motor_kind', side_effect=None
        ) as mock_set_motor_kind:
            response = client.post(
                '/motors/', json=stub_motor, params={'motor_kind': 'GENERIC'}
            )
            assert response.status_code == 200
            assert response.json() == {
                'motor_id': '123',
                'message': 'Motor successfully created',
            }
            mock_set_motor_kind.assert_called_once_with(MotorKinds.GENERIC)
            mock_create_motor.assert_called_once_with(Motor(**stub_motor))


def test_create_liquid_motor_level_tank(stub_motor, stub_level_tank):
    stub_motor.update({'tanks': [stub_level_tank]})
    with patch.object(
        MotorController,
        'create_motor',
        return_value=MotorCreated(motor_id='123'),
    ) as mock_create_motor:
        with patch.object(
            Motor, 'set_motor_kind', side_effect=None
        ) as mock_set_motor_kind:
            response = client.post(
                '/motors/', json=stub_motor, params={'motor_kind': 'LIQUID'}
            )
            assert response.status_code == 200
            assert response.json() == {
                'motor_id': '123',
                'message': 'Motor successfully created',
            }
            mock_set_motor_kind.assert_called_once_with(MotorKinds.LIQUID)
            mock_create_motor.assert_called_once_with(Motor(**stub_motor))


def test_create_liquid_motor_mass_flow_tank(stub_motor, stub_mass_flow_tank):
    stub_motor.update({'tanks': [stub_mass_flow_tank]})
    with patch.object(
        MotorController,
        'create_motor',
        return_value=MotorCreated(motor_id='123'),
    ) as mock_create_motor:
        with patch.object(
            Motor, 'set_motor_kind', side_effect=None
        ) as mock_set_motor_kind:
            response = client.post(
                '/motors/', json=stub_motor, params={'motor_kind': 'LIQUID'}
            )
            assert response.status_code == 200
            assert response.json() == {
                'motor_id': '123',
                'message': 'Motor successfully created',
            }
            mock_set_motor_kind.assert_called_once_with(MotorKinds.LIQUID)
            mock_create_motor.assert_called_once_with(Motor(**stub_motor))


def test_create_liquid_motor_ullage_tank(stub_motor, stub_ullage_tank):
    stub_motor.update({'tanks': [stub_ullage_tank]})
    with patch.object(
        MotorController,
        'create_motor',
        return_value=MotorCreated(motor_id='123'),
    ) as mock_create_motor:
        with patch.object(
            Motor, 'set_motor_kind', side_effect=None
        ) as mock_set_motor_kind:
            response = client.post(
                '/motors/', json=stub_motor, params={'motor_kind': 'LIQUID'}
            )
            assert response.status_code == 200
            assert response.json() == {
                'motor_id': '123',
                'message': 'Motor successfully created',
            }
            mock_set_motor_kind.assert_called_once_with(MotorKinds.LIQUID)
            mock_create_motor.assert_called_once_with(Motor(**stub_motor))


def test_create_liquid_motor_mass_tank(stub_motor, stub_mass_tank):
    stub_motor.update({'tanks': [stub_mass_tank]})
    with patch.object(
        MotorController,
        'create_motor',
        return_value=MotorCreated(motor_id='123'),
    ) as mock_create_motor:
        with patch.object(
            Motor, 'set_motor_kind', side_effect=None
        ) as mock_set_motor_kind:
            response = client.post(
                '/motors/', json=stub_motor, params={'motor_kind': 'LIQUID'}
            )
            assert response.status_code == 200
            assert response.json() == {
                'motor_id': '123',
                'message': 'Motor successfully created',
            }
            mock_set_motor_kind.assert_called_once_with(MotorKinds.LIQUID)
            mock_create_motor.assert_called_once_with(Motor(**stub_motor))


def test_create_hybrid_motor(stub_motor, stub_level_tank):
    stub_motor.update(
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
    with patch.object(
        MotorController,
        'create_motor',
        return_value=MotorCreated(motor_id='123'),
    ) as mock_create_motor:
        with patch.object(
            Motor, 'set_motor_kind', side_effect=None
        ) as mock_set_motor_kind:
            response = client.post(
                '/motors/', json=stub_motor, params={'motor_kind': 'HYBRID'}
            )
            assert response.status_code == 200
            assert response.json() == {
                'motor_id': '123',
                'message': 'Motor successfully created',
            }
            mock_set_motor_kind.assert_called_once_with(MotorKinds.HYBRID)
            mock_create_motor.assert_called_once_with(Motor(**stub_motor))


def test_create_solid_motor(stub_motor):
    stub_motor.update(
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
    with patch.object(
        MotorController,
        'create_motor',
        return_value=MotorCreated(motor_id='123'),
    ) as mock_create_motor:
        with patch.object(
            Motor, 'set_motor_kind', side_effect=None
        ) as mock_set_motor_kind:
            response = client.post(
                '/motors/', json=stub_motor, params={'motor_kind': 'SOLID'}
            )
            assert response.status_code == 200
            assert response.json() == {
                'motor_id': '123',
                'message': 'Motor successfully created',
            }
            mock_set_motor_kind.assert_called_once_with(MotorKinds.SOLID)
            mock_create_motor.assert_called_once_with(Motor(**stub_motor))


def test_create_motor_invalid_input():
    response = client.post(
        '/motors/', json={'burn_time': 'foo', 'nozzle_radius': 'bar'}
    )
    assert response.status_code == 422


def test_create_motor_server_error(stub_motor):
    with patch.object(
        MotorController,
        'create_motor',
        side_effect=HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    ):
        response = client.post(
            '/motors/', json=stub_motor, params={'motor_kind': 'HYBRID'}
        )
        assert response.status_code == 500
        assert response.json() == {'detail': 'Internal Server Error'}


def test_read_motor(stub_motor):
    stub_motor.update({'selected_motor_kind': 'HYBRID'})
    with patch.object(
        MotorController,
        'get_motor_by_id',
        return_value=MotorView(**stub_motor),
    ) as mock_read_motor:
        response = client.get('/motors/123')
        assert response.status_code == 200
        assert response.json() == stub_motor
        mock_read_motor.assert_called_once_with('123')


def test_read_motor_not_found():
    with patch.object(
        MotorController,
        'get_motor_by_id',
        side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND),
    ) as mock_read_motor:
        response = client.get('/motors/123')
        assert response.status_code == 404
        assert response.json() == {'detail': 'Not Found'}
        mock_read_motor.assert_called_once_with('123')


def test_read_motor_server_error():
    with patch.object(
        MotorController,
        'get_motor_by_id',
        side_effect=HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    ):
        response = client.get('/motors/123')
        assert response.status_code == 500
        assert response.json() == {'detail': 'Internal Server Error'}


def test_update_motor(stub_motor):
    with patch.object(
        MotorController,
        'update_motor_by_id',
        return_value=MotorUpdated(motor_id='123'),
    ) as mock_update_motor:
        with patch.object(
            Motor, 'set_motor_kind', side_effect=None
        ) as mock_set_motor_kind:
            response = client.put(
                '/motors/123', json=stub_motor, params={'motor_kind': 'HYBRID'}
            )
            assert response.status_code == 200
            assert response.json() == {
                'motor_id': '123',
                'message': 'Motor successfully updated',
            }
            mock_update_motor.assert_called_once_with(
                '123', Motor(**stub_motor)
            )
            mock_set_motor_kind.assert_called_once_with(MotorKinds.HYBRID)


def test_update_motor_invalid_input():
    response = client.put(
        '/motors/123',
        json={'burn_time': 'foo', 'nozzle_radius': 'bar'},
        params={'motor_kind': 'HYBRID'},
    )
    assert response.status_code == 422


def test_update_motor_not_found(stub_motor):
    with patch.object(
        MotorController,
        'update_motor_by_id',
        side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND),
    ):
        response = client.put(
            '/motors/123', json=stub_motor, params={'motor_kind': 'HYBRID'}
        )
        assert response.status_code == 404
        assert response.json() == {'detail': 'Not Found'}


def test_update_motor_server_error(stub_motor):
    with patch.object(
        MotorController,
        'update_motor_by_id',
        side_effect=HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    ):
        response = client.put(
            '/motors/123', json=stub_motor, params={'motor_kind': 'HYBRID'}
        )
        assert response.status_code == 500
        assert response.json() == {'detail': 'Internal Server Error'}


def test_delete_motor():
    with patch.object(
        MotorController,
        'delete_motor_by_id',
        return_value=MotorDeleted(motor_id='123'),
    ) as mock_delete_motor:
        response = client.delete('/motors/123')
        assert response.status_code == 200
        assert response.json() == {
            'motor_id': '123',
            'message': 'Motor successfully deleted',
        }
        mock_delete_motor.assert_called_once_with('123')


def test_delete_motor_server_error():
    with patch.object(
        MotorController,
        'delete_motor_by_id',
        side_effect=HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    ):
        response = client.delete('/motors/123')
        assert response.status_code == 500
        assert response.json() == {'detail': 'Internal Server Error'}


def test_simulate_motor(stub_motor_summary):
    with patch.object(
        MotorController,
        'simulate_motor',
        return_value=MotorSummary(**stub_motor_summary),
    ) as mock_simulate_motor:
        response = client.get('/motors/123/summary')
        assert response.status_code == 200
        assert response.json() == stub_motor_summary
        mock_simulate_motor.assert_called_once_with('123')


def test_simulate_motor_not_found():
    with patch.object(
        MotorController,
        'simulate_motor',
        side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND),
    ) as mock_simulate_motor:
        response = client.get('/motors/123/summary')
        assert response.status_code == 404
        assert response.json() == {'detail': 'Not Found'}
        mock_simulate_motor.assert_called_once_with('123')


def test_simulate_motor_server_error():
    with patch.object(
        MotorController,
        'simulate_motor',
        side_effect=HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    ):
        response = client.get('/motors/123/summary')
        assert response.status_code == 500
        assert response.json() == {'detail': 'Internal Server Error'}


def test_read_rocketpy_motor():
    with patch.object(
        MotorController, 'get_rocketpy_motor_binary', return_value=b'rocketpy'
    ) as mock_read_rocketpy_motor:
        response = client.get('/motors/123/rocketpy')
        assert response.status_code == 203
        assert response.content == b'rocketpy'
        assert response.headers['content-type'] == 'application/octet-stream'
        mock_read_rocketpy_motor.assert_called_once_with('123')


def test_read_rocketpy_motor_not_found():
    with patch.object(
        MotorController,
        'get_rocketpy_motor_binary',
        side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND),
    ) as mock_read_rocketpy_motor:
        response = client.get('/motors/123/rocketpy')
        assert response.status_code == 404
        assert response.json() == {'detail': 'Not Found'}
        mock_read_rocketpy_motor.assert_called_once_with('123')


def test_read_rocketpy_motor_server_error():
    with patch.object(
        MotorController,
        'get_rocketpy_motor_binary',
        side_effect=HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    ):
        response = client.get('/motors/123/rocketpy')
        assert response.status_code == 500
        assert response.json() == {'detail': 'Internal Server Error'}
