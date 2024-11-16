from unittest.mock import patch
import json
import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from lib.models.aerosurfaces import (
    Fins,
    NoseCone,
    Tail,
    RailButtons,
    Parachute,
)
from lib.models.rocket import Rocket
from lib.models.motor import (
    Motor,
    MotorKinds,
    MotorTank,
    TankFluids,
    TankKinds,
)
from lib.controllers.rocket import RocketController
from lib.views.motor import MotorView
from lib.views.rocket import (
    RocketCreated,
    RocketUpdated,
    RocketDeleted,
    RocketSummary,
    RocketView,
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
def stub_rocket_summary():
    rocket_summary = RocketSummary()
    rocket_summary_json = rocket_summary.model_dump_json()
    return json.loads(rocket_summary_json)


@pytest.fixture
def stub_nose_cone():
    nose_cone = NoseCone(
        name='nose',
        length=0,
        kind='kind',
        position=0,
        base_radius=0,
        rocket_radius=0,
    )
    nose_cone_json = nose_cone.model_dump_json()
    return json.loads(nose_cone_json)


@pytest.fixture
def stub_fins():
    fins = Fins(
        fins_kind='TRAPEZOIDAL',
        name='fins',
        n=0,
        root_chord=0,
        span=0,
        position=0,
    )
    fins_json = fins.model_dump_json()
    return json.loads(fins_json)


@pytest.fixture
def stub_tail():
    tail = Tail(
        name='tail',
        top_radius=0,
        bottom_radius=0,
        length=0,
        position=0,
        radius=0,
    )
    tail_json = tail.model_dump_json()
    return json.loads(tail_json)


@pytest.fixture
def stub_rail_buttons():
    rail_buttons = RailButtons(
        upper_button_position=0,
        lower_button_position=0,
        angular_position=0,
    )
    rail_buttons_json = rail_buttons.model_dump_json()
    return json.loads(rail_buttons_json)


@pytest.fixture
def stub_parachute():
    parachute = Parachute(
        name='parachute',
        cd_s=0,
        sampling_rate=0,
        lag=0,
        trigger='trigger',
        noise=(0, 0, 0),
    )
    parachute_json = parachute.model_dump_json()
    return json.loads(parachute_json)


@pytest.fixture
def stub_rocket(stub_motor):
    rocket = Rocket(
        motor=stub_motor,
        radius=0,
        mass=0,
        motor_position=0,
        center_of_mass_without_motor=0,
        inertia=[0, 0, 0],
        power_off_drag=[(0, 0)],
        power_on_drag=[(0, 0)],
        coordinate_system_orientation='TAIL_TO_NOSE',
    )
    rocket_json = rocket.model_dump_json()
    return json.loads(rocket_json)


def test_create_rocket(stub_rocket):
    with patch.object(
        RocketController,
        'create_rocket',
        return_value=RocketCreated(rocket_id='123'),
    ) as mock_create_rocket:
        with patch.object(
            Motor, 'set_motor_kind', side_effect=None
        ) as mock_set_motor_kind:
            response = client.post(
                '/rockets/', json=stub_rocket, params={'motor_kind': 'HYBRID'}
            )
            assert response.status_code == 200
            assert response.json() == {
                'rocket_id': '123',
                'message': 'Rocket successfully created',
            }
            mock_set_motor_kind.assert_called_once_with(MotorKinds.HYBRID)
            mock_create_rocket.assert_called_once_with(Rocket(**stub_rocket))


def test_create_rocket_optional_params(
    stub_rocket,
    stub_nose_cone,
    stub_fins,
    stub_tail,
    stub_rail_buttons,
    stub_parachute,
):
    stub_rocket.update(
        {
            'parachutes': [stub_parachute],
            'rail_buttons': stub_rail_buttons,
            'nose': stub_nose_cone,
            'fins': [stub_fins],
            'tail': stub_tail,
        }
    )
    with patch.object(
        RocketController,
        'create_rocket',
        return_value=RocketCreated(rocket_id='123'),
    ) as mock_create_rocket:
        with patch.object(
            Motor, 'set_motor_kind', side_effect=None
        ) as mock_set_motor_kind:
            response = client.post(
                '/rockets/', json=stub_rocket, params={'motor_kind': 'HYBRID'}
            )
            assert response.status_code == 200
            assert response.json() == {
                'rocket_id': '123',
                'message': 'Rocket successfully created',
            }
            mock_set_motor_kind.assert_called_once_with(MotorKinds.HYBRID)
            mock_create_rocket.assert_called_once_with(Rocket(**stub_rocket))


def test_create_generic_motor_rocket(stub_rocket, stub_motor):
    stub_motor.update(
        {
            'chamber_radius': 0,
            'chamber_height': 0,
            'chamber_position': 0,
            'propellant_initial_mass': 0,
            'nozzle_position': 0,
        }
    )
    stub_rocket.update({'motor': stub_motor})
    with patch.object(
        RocketController,
        'create_rocket',
        return_value=RocketCreated(rocket_id='123'),
    ) as mock_create_rocket:
        with patch.object(
            Motor, 'set_motor_kind', side_effect=None
        ) as mock_set_motor_kind:
            response = client.post(
                '/rockets/', json=stub_rocket, params={'motor_kind': 'GENERIC'}
            )
            assert response.status_code == 200
            assert response.json() == {
                'rocket_id': '123',
                'message': 'Rocket successfully created',
            }
            mock_set_motor_kind.assert_called_once_with(MotorKinds.GENERIC)
            mock_create_rocket.assert_called_once_with(Rocket(**stub_rocket))


def test_create_liquid_motor_level_tank_rocket(
    stub_rocket, stub_motor, stub_level_tank
):
    stub_motor.update({'tanks': [stub_level_tank]})
    stub_rocket.update({'motor': stub_motor})
    with patch.object(
        RocketController,
        'create_rocket',
        return_value=RocketCreated(rocket_id='123'),
    ) as mock_create_rocket:
        with patch.object(
            Motor, 'set_motor_kind', side_effect=None
        ) as mock_set_motor_kind:
            response = client.post(
                '/rockets/', json=stub_rocket, params={'motor_kind': 'LIQUID'}
            )
            assert response.status_code == 200
            assert response.json() == {
                'rocket_id': '123',
                'message': 'Rocket successfully created',
            }
            mock_set_motor_kind.assert_called_once_with(MotorKinds.LIQUID)
            mock_create_rocket.assert_called_once_with(Rocket(**stub_rocket))


def test_create_liquid_motor_mass_flow_tank_rocket(
    stub_rocket, stub_motor, stub_mass_flow_tank
):
    stub_motor.update({'tanks': [stub_mass_flow_tank]})
    stub_rocket.update({'motor': stub_motor})
    with patch.object(
        RocketController,
        'create_rocket',
        return_value=RocketCreated(rocket_id='123'),
    ) as mock_create_rocket:
        with patch.object(
            Motor, 'set_motor_kind', side_effect=None
        ) as mock_set_motor_kind:
            response = client.post(
                '/rockets/', json=stub_rocket, params={'motor_kind': 'LIQUID'}
            )
            assert response.status_code == 200
            assert response.json() == {
                'rocket_id': '123',
                'message': 'Rocket successfully created',
            }
            mock_set_motor_kind.assert_called_once_with(MotorKinds.LIQUID)
            mock_create_rocket.assert_called_once_with(Rocket(**stub_rocket))


def test_create_liquid_motor_ullage_tank_rocket(
    stub_rocket, stub_motor, stub_ullage_tank
):
    stub_motor.update({'tanks': [stub_ullage_tank]})
    stub_rocket.update({'motor': stub_motor})
    with patch.object(
        RocketController,
        'create_rocket',
        return_value=RocketCreated(rocket_id='123'),
    ) as mock_create_rocket:
        with patch.object(
            Motor, 'set_motor_kind', side_effect=None
        ) as mock_set_motor_kind:
            response = client.post(
                '/rockets/', json=stub_rocket, params={'motor_kind': 'LIQUID'}
            )
            assert response.status_code == 200
            assert response.json() == {
                'rocket_id': '123',
                'message': 'Rocket successfully created',
            }
            mock_set_motor_kind.assert_called_once_with(MotorKinds.LIQUID)
            mock_create_rocket.assert_called_once_with(Rocket(**stub_rocket))


def test_create_liquid_motor_mass_tank_rocket(
    stub_rocket, stub_motor, stub_mass_tank
):
    stub_motor.update({'tanks': [stub_mass_tank]})
    stub_rocket.update({'motor': stub_motor})
    with patch.object(
        RocketController,
        'create_rocket',
        return_value=RocketCreated(rocket_id='123'),
    ) as mock_create_rocket:
        with patch.object(
            Motor, 'set_motor_kind', side_effect=None
        ) as mock_set_motor_kind:
            response = client.post(
                '/rockets/', json=stub_rocket, params={'motor_kind': 'LIQUID'}
            )
            assert response.status_code == 200
            assert response.json() == {
                'rocket_id': '123',
                'message': 'Rocket successfully created',
            }
            mock_set_motor_kind.assert_called_once_with(MotorKinds.LIQUID)
            mock_create_rocket.assert_called_once_with(Rocket(**stub_rocket))


def test_create_hybrid_motor_rocket(stub_rocket, stub_motor, stub_level_tank):
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
    stub_rocket.update({'motor': stub_motor})
    with patch.object(
        RocketController,
        'create_rocket',
        return_value=RocketCreated(rocket_id='123'),
    ) as mock_create_rocket:
        with patch.object(
            Motor, 'set_motor_kind', side_effect=None
        ) as mock_set_motor_kind:
            response = client.post(
                '/rockets/', json=stub_rocket, params={'motor_kind': 'HYBRID'}
            )
            assert response.status_code == 200
            assert response.json() == {
                'rocket_id': '123',
                'message': 'Rocket successfully created',
            }
            mock_set_motor_kind.assert_called_once_with(MotorKinds.HYBRID)
            mock_create_rocket.assert_called_once_with(Rocket(**stub_rocket))


def test_create_solid_motor_rocket(stub_rocket, stub_motor):
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
    stub_rocket.update({'motor': stub_motor})
    with patch.object(
        RocketController,
        'create_rocket',
        return_value=RocketCreated(rocket_id='123'),
    ) as mock_create_rocket:
        with patch.object(
            Motor, 'set_motor_kind', side_effect=None
        ) as mock_set_motor_kind:
            response = client.post(
                '/rockets/', json=stub_rocket, params={'motor_kind': 'SOLID'}
            )
            assert response.status_code == 200
            assert response.json() == {
                'rocket_id': '123',
                'message': 'Rocket successfully created',
            }
            mock_set_motor_kind.assert_called_once_with(MotorKinds.SOLID)
            mock_create_rocket.assert_called_once_with(Rocket(**stub_rocket))


def test_create_rocket_invalid_input():
    response = client.post('/rockets/', json={'radius': 'foo', 'mass': 'bar'})
    assert response.status_code == 422


def test_create_rocket_server_error(stub_rocket):
    with patch.object(
        RocketController,
        'create_rocket',
        side_effect=HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    ):
        response = client.post(
            '/rockets/', json=stub_rocket, params={'motor_kind': 'HYBRID'}
        )
        assert response.status_code == 500
        assert response.json() == {'detail': 'Internal Server Error'}


def test_read_rocket(stub_rocket, stub_motor):
    motor_view = MotorView(**stub_motor, selected_motor_kind=MotorKinds.HYBRID)
    stub_rocket.update(motor=motor_view)
    rocket_view = RocketView(**stub_rocket)
    with patch.object(
        RocketController,
        'get_rocket_by_id',
        return_value=rocket_view,
    ) as mock_read_rocket:
        response = client.get('/rockets/123')
        assert response.status_code == 200
        assert response.json() == json.loads(rocket_view.model_dump_json())
        mock_read_rocket.assert_called_once_with('123')


def test_read_rocket_not_found():
    with patch.object(
        RocketController,
        'get_rocket_by_id',
        side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND),
    ) as mock_read_rocket:
        response = client.get('/rockets/123')
        assert response.status_code == 404
        assert response.json() == {'detail': 'Not Found'}
        mock_read_rocket.assert_called_once_with('123')


def test_read_rocket_server_error():
    with patch.object(
        RocketController,
        'get_rocket_by_id',
        side_effect=HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    ):
        response = client.get('/rockets/123')
        assert response.status_code == 500
        assert response.json() == {'detail': 'Internal Server Error'}


def test_update_rocket(stub_rocket):
    with patch.object(
        RocketController,
        'update_rocket_by_id',
        return_value=RocketUpdated(rocket_id='123'),
    ) as mock_update_rocket:
        with patch.object(
            Motor, 'set_motor_kind', side_effect=None
        ) as mock_set_motor_kind:
            response = client.put(
                '/rockets/123',
                json=stub_rocket,
                params={'motor_kind': 'GENERIC'},
            )
            assert response.status_code == 200
            assert response.json() == {
                'rocket_id': '123',
                'message': 'Rocket successfully updated',
            }
            mock_update_rocket.assert_called_once_with(
                '123', Rocket(**stub_rocket)
            )
            mock_set_motor_kind.assert_called_once_with(MotorKinds.GENERIC)


def test_update_rocket_invalid_input():
    response = client.put(
        '/rockets/123',
        json={'mass': 'foo', 'radius': 'bar'},
        params={'motor_kind': 'GENERIC'},
    )
    assert response.status_code == 422


def test_update_rocket_not_found(stub_rocket):
    with patch.object(
        RocketController,
        'update_rocket_by_id',
        side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND),
    ):
        response = client.put(
            '/rockets/123', json=stub_rocket, params={'motor_kind': 'HYBRID'}
        )
        assert response.status_code == 404
        assert response.json() == {'detail': 'Not Found'}


def test_update_rocket_server_error(stub_rocket):
    with patch.object(
        RocketController,
        'update_rocket_by_id',
        side_effect=HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    ):
        response = client.put(
            '/rockets/123', json=stub_rocket, params={'motor_kind': 'HYBRID'}
        )
        assert response.status_code == 500
        assert response.json() == {'detail': 'Internal Server Error'}


def test_delete_rocket():
    with patch.object(
        RocketController,
        'delete_rocket_by_id',
        return_value=RocketDeleted(rocket_id='123'),
    ) as mock_delete_rocket:
        response = client.delete('/rockets/123')
        assert response.status_code == 200
        assert response.json() == {
            'rocket_id': '123',
            'message': 'Rocket successfully deleted',
        }
        mock_delete_rocket.assert_called_once_with('123')


def test_delete_rocket_server_error():
    with patch.object(
        RocketController,
        'delete_rocket_by_id',
        side_effect=HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    ):
        response = client.delete('/rockets/123')
        assert response.status_code == 500
        assert response.json() == {'detail': 'Internal Server Error'}


def test_simulate_rocket(stub_rocket_summary):
    with patch.object(
        RocketController,
        'simulate_rocket',
        return_value=RocketSummary(**stub_rocket_summary),
    ) as mock_simulate_rocket:
        response = client.get('/rockets/123/summary')
        assert response.status_code == 200
        assert response.json() == stub_rocket_summary
        mock_simulate_rocket.assert_called_once_with('123')


def test_simulate_rocket_not_found():
    with patch.object(
        RocketController,
        'simulate_rocket',
        side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND),
    ) as mock_simulate_rocket:
        response = client.get('/rockets/123/summary')
        assert response.status_code == 404
        assert response.json() == {'detail': 'Not Found'}
        mock_simulate_rocket.assert_called_once_with('123')


def test_simulate_rocket_server_error():
    with patch.object(
        RocketController,
        'simulate_rocket',
        side_effect=HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    ):
        response = client.get('/rockets/123/summary')
        assert response.status_code == 500
        assert response.json() == {'detail': 'Internal Server Error'}


def test_read_rocketpy_rocket():
    with patch.object(
        RocketController,
        'get_rocketpy_rocket_binary',
        return_value=b'rocketpy',
    ) as mock_read_rocketpy_rocket:
        response = client.get('/rockets/123/rocketpy')
        assert response.status_code == 203
        assert response.content == b'rocketpy'
        assert response.headers['content-type'] == 'application/octet-stream'
        mock_read_rocketpy_rocket.assert_called_once_with('123')


def test_read_rocketpy_rocket_not_found():
    with patch.object(
        RocketController,
        'get_rocketpy_rocket_binary',
        side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND),
    ) as mock_read_rocketpy_rocket:
        response = client.get('/rockets/123/rocketpy')
        assert response.status_code == 404
        assert response.json() == {'detail': 'Not Found'}
        mock_read_rocketpy_rocket.assert_called_once_with('123')


def test_read_rocketpy_rocket_server_error():
    with patch.object(
        RocketController,
        'get_rocketpy_rocket_binary',
        side_effect=HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    ):
        response = client.get('/rockets/123/rocketpy')
        assert response.status_code == 500
        assert response.json() == {'detail': 'Internal Server Error'}
