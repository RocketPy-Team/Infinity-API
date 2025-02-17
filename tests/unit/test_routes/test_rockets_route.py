from unittest.mock import patch, Mock, AsyncMock
import json
import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from src.models.sub.aerosurfaces import (
    Tail,
    RailButtons,
    Parachute,
)
from src.models.rocket import RocketModel
from src.models.motor import (
    MotorModel,
    MotorKinds,
)
from src.views.rocket import (
    RocketCreated,
    RocketRetrieved,
    RocketSimulation,
    RocketView,
)
from src import app

client = TestClient(app)


@pytest.fixture
def stub_rocket_simulation_dump():
    rocket_simulation = RocketSimulation()
    rocket_simulation_json = rocket_simulation.model_dump_json()
    return json.loads(rocket_simulation_json)


@pytest.fixture
def stub_tail_dump():
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
def stub_rail_buttons_dump():
    rail_buttons = RailButtons(
        upper_button_position=0,
        lower_button_position=0,
        angular_position=0,
    )
    rail_buttons_json = rail_buttons.model_dump_json()
    return json.loads(rail_buttons_json)


@pytest.fixture
def stub_parachute_dump():
    parachute = Parachute(
        name='parachute',
        cd_s=0,
        sampling_rate=1,
        lag=0,
        trigger='trigger',
        noise=(0, 0, 0),
    )
    parachute_json = parachute.model_dump_json()
    return json.loads(parachute_json)


@pytest.fixture(autouse=True)
def mock_controller_instance():
    with patch(
        "src.routes.rocket.RocketController", autospec=True
    ) as mock_controller:
        mock_controller_instance = mock_controller.return_value
        mock_controller_instance.post_rocket = Mock()
        mock_controller_instance.get_rocket_by_id = Mock()
        mock_controller_instance.put_rocket_by_id = Mock()
        mock_controller_instance.delete_rocket_by_id = Mock()
        mock_controller_instance.get_rocket_simulation = Mock()
        mock_controller_instance.get_rocketpy_rocket_binary = Mock()
        yield mock_controller_instance


def test_create_rocket(stub_rocket_dump, mock_controller_instance):
    mock_response = AsyncMock(return_value=RocketCreated(rocket_id='123'))
    mock_controller_instance.post_rocket = mock_response
    with patch.object(
        MotorModel, 'set_motor_kind', side_effect=None
    ) as mock_set_motor_kind:
        response = client.post(
            '/rockets/', json=stub_rocket_dump, params={'motor_kind': 'HYBRID'}
        )
        assert response.status_code == 201
        assert response.json() == {
            'rocket_id': '123',
            'message': 'Rocket successfully created',
        }
        mock_set_motor_kind.assert_called_once_with(MotorKinds.HYBRID)
        mock_controller_instance.post_rocket.assert_called_once_with(
            RocketModel(**stub_rocket_dump)
        )


def test_create_rocket_optional_params(
    stub_rocket_dump,
    stub_tail_dump,
    stub_rail_buttons_dump,
    stub_parachute_dump,
    mock_controller_instance,
):
    stub_rocket_dump.update(
        {
            'parachutes': [stub_parachute_dump],
            'rail_buttons': stub_rail_buttons_dump,
            'tail': stub_tail_dump,
        }
    )
    mock_response = AsyncMock(return_value=RocketCreated(rocket_id='123'))
    mock_controller_instance.post_rocket = mock_response
    with patch.object(
        MotorModel, 'set_motor_kind', side_effect=None
    ) as mock_set_motor_kind:
        response = client.post(
            '/rockets/', json=stub_rocket_dump, params={'motor_kind': 'HYBRID'}
        )
        assert response.status_code == 201
        assert response.json() == {
            'rocket_id': '123',
            'message': 'Rocket successfully created',
        }
        mock_set_motor_kind.assert_called_once_with(MotorKinds.HYBRID)
        mock_controller_instance.post_rocket.assert_called_once_with(
            RocketModel(**stub_rocket_dump)
        )


def test_create_generic_motor_rocket(
    stub_rocket_dump, stub_motor_dump, mock_controller_instance
):
    stub_motor_dump.update(
        {
            'chamber_radius': 0,
            'chamber_height': 0,
            'chamber_position': 0,
            'propellant_initial_mass': 0,
            'nozzle_position': 0,
        }
    )
    stub_rocket_dump.update({'motor': stub_motor_dump})
    mock_response = AsyncMock(return_value=RocketCreated(rocket_id='123'))
    mock_controller_instance.post_rocket = mock_response
    with patch.object(
        MotorModel, 'set_motor_kind', side_effect=None
    ) as mock_set_motor_kind:
        response = client.post(
            '/rockets/',
            json=stub_rocket_dump,
            params={'motor_kind': 'GENERIC'},
        )
        assert response.status_code == 201
        assert response.json() == {
            'rocket_id': '123',
            'message': 'Rocket successfully created',
        }
        mock_set_motor_kind.assert_called_once_with(MotorKinds.GENERIC)
        mock_controller_instance.post_rocket.assert_called_once_with(
            RocketModel(**stub_rocket_dump)
        )


def test_create_liquid_motor_level_tank_rocket(
    stub_rocket_dump,
    stub_motor_dump,
    stub_level_tank_dump,
    mock_controller_instance,
):
    stub_motor_dump.update({'tanks': [stub_level_tank_dump]})
    stub_rocket_dump.update({'motor': stub_motor_dump})
    mock_response = AsyncMock(return_value=RocketCreated(rocket_id='123'))
    mock_controller_instance.post_rocket = mock_response
    with patch.object(
        MotorModel, 'set_motor_kind', side_effect=None
    ) as mock_set_motor_kind:
        response = client.post(
            '/rockets/', json=stub_rocket_dump, params={'motor_kind': 'LIQUID'}
        )
        assert response.status_code == 201
        assert response.json() == {
            'rocket_id': '123',
            'message': 'Rocket successfully created',
        }
        mock_set_motor_kind.assert_called_once_with(MotorKinds.LIQUID)
        mock_controller_instance.post_rocket.assert_called_once_with(
            RocketModel(**stub_rocket_dump)
        )


def test_create_liquid_motor_mass_flow_tank_rocket(
    stub_rocket_dump,
    stub_motor_dump,
    stub_mass_flow_tank_dump,
    mock_controller_instance,
):
    stub_motor_dump.update({'tanks': [stub_mass_flow_tank_dump]})
    stub_rocket_dump.update({'motor': stub_motor_dump})
    mock_response = AsyncMock(return_value=RocketCreated(rocket_id='123'))
    mock_controller_instance.post_rocket = mock_response
    with patch.object(
        MotorModel, 'set_motor_kind', side_effect=None
    ) as mock_set_motor_kind:
        response = client.post(
            '/rockets/', json=stub_rocket_dump, params={'motor_kind': 'LIQUID'}
        )
        assert response.status_code == 201
        assert response.json() == {
            'rocket_id': '123',
            'message': 'Rocket successfully created',
        }
        mock_set_motor_kind.assert_called_once_with(MotorKinds.LIQUID)
        mock_controller_instance.post_rocket.assert_called_once_with(
            RocketModel(**stub_rocket_dump)
        )


def test_create_liquid_motor_ullage_tank_rocket(
    stub_rocket_dump,
    stub_motor_dump,
    stub_ullage_tank_dump,
    mock_controller_instance,
):
    stub_motor_dump.update({'tanks': [stub_ullage_tank_dump]})
    stub_rocket_dump.update({'motor': stub_motor_dump})
    mock_response = AsyncMock(return_value=RocketCreated(rocket_id='123'))
    mock_controller_instance.post_rocket = mock_response
    with patch.object(
        MotorModel, 'set_motor_kind', side_effect=None
    ) as mock_set_motor_kind:
        response = client.post(
            '/rockets/', json=stub_rocket_dump, params={'motor_kind': 'LIQUID'}
        )
        assert response.status_code == 201
        assert response.json() == {
            'rocket_id': '123',
            'message': 'Rocket successfully created',
        }
        mock_set_motor_kind.assert_called_once_with(MotorKinds.LIQUID)
        mock_controller_instance.post_rocket.assert_called_once_with(
            RocketModel(**stub_rocket_dump)
        )


def test_create_liquid_motor_mass_tank_rocket(
    stub_rocket_dump,
    stub_motor_dump,
    stub_mass_tank_dump,
    mock_controller_instance,
):
    stub_motor_dump.update({'tanks': [stub_mass_tank_dump]})
    stub_rocket_dump.update({'motor': stub_motor_dump})
    mock_response = AsyncMock(return_value=RocketCreated(rocket_id='123'))
    mock_controller_instance.post_rocket = mock_response
    with patch.object(
        MotorModel, 'set_motor_kind', side_effect=None
    ) as mock_set_motor_kind:
        response = client.post(
            '/rockets/', json=stub_rocket_dump, params={'motor_kind': 'LIQUID'}
        )
        assert response.status_code == 201
        assert response.json() == {
            'rocket_id': '123',
            'message': 'Rocket successfully created',
        }
        mock_set_motor_kind.assert_called_once_with(MotorKinds.LIQUID)
        mock_controller_instance.post_rocket.assert_called_once_with(
            RocketModel(**stub_rocket_dump)
        )


def test_create_hybrid_motor_rocket(
    stub_rocket_dump,
    stub_motor_dump,
    stub_level_tank_dump,
    mock_controller_instance,
):
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
            'tanks': [stub_level_tank_dump],
        }
    )
    stub_rocket_dump.update({'motor': stub_motor_dump})
    mock_response = AsyncMock(return_value=RocketCreated(rocket_id='123'))
    mock_controller_instance.post_rocket = mock_response
    with patch.object(
        MotorModel, 'set_motor_kind', side_effect=None
    ) as mock_set_motor_kind:
        response = client.post(
            '/rockets/', json=stub_rocket_dump, params={'motor_kind': 'HYBRID'}
        )
        assert response.status_code == 201
        assert response.json() == {
            'rocket_id': '123',
            'message': 'Rocket successfully created',
        }
        mock_set_motor_kind.assert_called_once_with(MotorKinds.HYBRID)
        mock_controller_instance.post_rocket.assert_called_once_with(
            RocketModel(**stub_rocket_dump)
        )


def test_create_solid_motor_rocket(
    stub_rocket_dump, stub_motor_dump, mock_controller_instance
):
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
    stub_rocket_dump.update({'motor': stub_motor_dump})
    mock_response = AsyncMock(return_value=RocketCreated(rocket_id='123'))
    mock_controller_instance.post_rocket = mock_response
    with patch.object(
        MotorModel, 'set_motor_kind', side_effect=None
    ) as mock_set_motor_kind:
        response = client.post(
            '/rockets/', json=stub_rocket_dump, params={'motor_kind': 'SOLID'}
        )
        assert response.status_code == 201
        assert response.json() == {
            'rocket_id': '123',
            'message': 'Rocket successfully created',
        }
        mock_set_motor_kind.assert_called_once_with(MotorKinds.SOLID)
        mock_controller_instance.post_rocket.assert_called_once_with(
            RocketModel(**stub_rocket_dump)
        )


def test_create_rocket_invalid_input():
    response = client.post('/rockets/', json={'radius': 'foo', 'mass': 'bar'})
    assert response.status_code == 422


def test_create_rocket_server_error(
    stub_rocket_dump, mock_controller_instance
):
    mock_controller_instance.post_rocket.side_effect = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    response = client.post(
        '/rockets/', json=stub_rocket_dump, params={'motor_kind': 'HYBRID'}
    )
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}


def test_read_rocket(
    stub_rocket_dump, stub_motor_dump, mock_controller_instance
):
    stub_rocket_dump.update({'motor': stub_motor_dump})
    rocket_view = RocketView(rocket_id='123', **stub_rocket_dump)
    mock_response = AsyncMock(return_value=RocketRetrieved(rocket=rocket_view))
    mock_controller_instance.get_rocket_by_id = mock_response
    response = client.get('/rockets/123')
    assert response.status_code == 200
    assert response.json() == {
        'message': 'Rocket successfully retrieved',
        'rocket': json.loads(rocket_view.model_dump_json()),
    }
    mock_controller_instance.get_rocket_by_id.assert_called_once_with('123')


def test_read_rocket_not_found(mock_controller_instance):
    mock_controller_instance.get_rocket_by_id.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND
    )
    response = client.get('/rockets/123')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}


def test_read_rocket_server_error(mock_controller_instance):
    mock_controller_instance.get_rocket_by_id.side_effect = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    response = client.get('/rockets/123')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}


def test_update_rocket(stub_rocket_dump, mock_controller_instance):
    mock_response = AsyncMock(return_value=None)
    mock_controller_instance.put_rocket_by_id = mock_response
    with patch.object(
        MotorModel, 'set_motor_kind', side_effect=None
    ) as mock_set_motor_kind:
        response = client.put(
            '/rockets/123',
            json=stub_rocket_dump,
            params={'motor_kind': 'HYBRID'},
        )
        assert response.status_code == 204
        mock_set_motor_kind.assert_called_once_with(MotorKinds.HYBRID)
        mock_controller_instance.put_rocket_by_id.assert_called_once_with(
            '123', RocketModel(**stub_rocket_dump)
        )


def test_update_rocket_invalid_input():
    response = client.put(
        '/rockets/123',
        json={'mass': 'foo', 'radius': 'bar'},
        params={'motor_kind': 'GENERIC'},
    )
    assert response.status_code == 422


def test_update_rocket_not_found(stub_rocket_dump, mock_controller_instance):
    mock_controller_instance.put_rocket_by_id.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND
    )
    response = client.put(
        '/rockets/123',
        json=stub_rocket_dump,
        params={'motor_kind': 'HYBRID'},
    )
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}


def test_update_rocket_server_error(
    stub_rocket_dump, mock_controller_instance
):
    mock_controller_instance.put_rocket_by_id.side_effect = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    response = client.put(
        '/rockets/123',
        json=stub_rocket_dump,
        params={'motor_kind': 'HYBRID'},
    )
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}


def test_delete_rocket(mock_controller_instance):
    mock_response = AsyncMock(return_value=None)
    mock_controller_instance.delete_rocket_by_id = mock_response
    response = client.delete('/rockets/123')
    assert response.status_code == 204
    mock_controller_instance.delete_rocket_by_id.assert_called_once_with('123')


def test_delete_rocket_server_error(mock_controller_instance):
    mock_controller_instance.delete_rocket_by_id.side_effect = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    response = client.delete('/rockets/123')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}


def test_get_rocket_simulation(
    stub_rocket_simulation_dump, mock_controller_instance
):
    mock_response = AsyncMock(
        return_value=RocketSimulation(**stub_rocket_simulation_dump)
    )
    mock_controller_instance.get_rocket_simulation = mock_response
    response = client.get('/rockets/123/simulate')
    assert response.status_code == 200
    assert response.json() == stub_rocket_simulation_dump
    mock_controller_instance.get_rocket_simulation.assert_called_once_with(
        '123'
    )


def test_get_rocket_simulation_not_found(mock_controller_instance):
    mock_controller_instance.get_rocket_simulation.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND
    )
    response = client.get('/rockets/123/simulate')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}


def test_get_rocket_simulation_server_error(mock_controller_instance):
    mock_controller_instance.get_rocket_simulation.side_effect = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    response = client.get('/rockets/123/simulate')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}


def test_read_rocketpy_rocket_binary(mock_controller_instance):
    mock_response = AsyncMock(return_value=b'rocketpy')
    mock_controller_instance.get_rocketpy_rocket_binary = mock_response
    response = client.get('/rockets/123/rocketpy')
    assert response.status_code == 203
    assert response.content == b'rocketpy'
    assert response.headers['content-type'] == 'application/octet-stream'
    mock_controller_instance.get_rocketpy_rocket_binary.assert_called_once_with(
        '123'
    )


def test_read_rocketpy_rocket_binary_not_found(mock_controller_instance):
    mock_controller_instance.get_rocketpy_rocket_binary.side_effect = (
        HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    )
    response = client.get('/rockets/123/rocketpy')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}


def test_read_rocketpy_rocket_binary_server_error(mock_controller_instance):
    mock_controller_instance.get_rocketpy_rocket_binary.side_effect = (
        HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    )
    response = client.get('/rockets/123/rocketpy')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal Server Error'}
