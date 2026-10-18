"""A rocket may exist before its motor does.

Jarvis creates the rocket entity as soon as the user saves the airframe,
often before any motor has been configured. It used to embed a placeholder
GENERIC motor with null fields, which made every drawing / simulate call
fail. RocketPy's own answer to "no motor yet" is `EmptyMotor` (a Rocket is
constructed with one by default), so Infinity accepts `motor: null` and
leaves the EmptyMotor in place.
"""

import pytest
from fastapi import HTTPException
from rocketpy.motors.empty_motor import EmptyMotor

from src.models.flight import FlightModel
from src.models.rocket import RocketModel
from src.services.flight import FlightService
from src.services.rocket import RocketService

ROCKET_WITHOUT_MOTOR = {
    'motor': None,
    'radius': 0.055,
    'mass': 5.65,
    'motor_position': 0.0,
    'center_of_mass_without_motor': 0.844,
    'inertia': [1.806, 1.806, 0.0183],
    'power_off_drag': [[0, 0.35], [1, 0.35]],
    'power_on_drag': [[0, 0.35], [1, 0.35]],
    'nose': {
        'name': 'Nose',
        'length': 0.2,
        'kind': 'elliptical',
        'position': 1.84,
        'base_radius': 0.055,
        'rocket_radius': 0.055,
    },
    'fins': [
        {
            'fins_kind': 'trapezoidal',
            'name': 'Fins',
            'n': 4,
            'root_chord': 0.17,
            'tip_chord': 0.14,
            'span': 0.0768,
            'position': 0.148,
            'rocket_radius': 0.055,
        }
    ],
    'tail': {
        'name': 'Tail',
        'top_radius': 0.055,
        'bottom_radius': 0.03,
        'length': 0.15,
        'position': 0.0,
        'radius': 0.055,
    },
}


def test_model_accepts_missing_motor():
    rocket = RocketModel(**ROCKET_WITHOUT_MOTOR)
    assert rocket.motor is None
    omitted = {k: v for k, v in ROCKET_WITHOUT_MOTOR.items() if k != 'motor'}
    assert RocketModel(**omitted).motor is None


def test_service_builds_rocket_with_empty_motor():
    service = RocketService.from_rocket_model(
        RocketModel(**ROCKET_WITHOUT_MOTOR)
    )
    assert isinstance(service.rocket.motor, EmptyMotor)


def test_drawing_geometry_works_without_motor():
    service = RocketService.from_rocket_model(
        RocketModel(**ROCKET_WITHOUT_MOTOR)
    )
    geometry = service.get_drawing_geometry()
    assert len(geometry.nose_cones) == 1
    assert len(geometry.fins) == 1
    assert len(geometry.tails) == 1
    # EmptyMotor contributes no patches but the envelope stays well-formed.
    assert geometry.motor is None or geometry.motor.patches == []


def test_rocket_simulation_without_motor_is_422():
    service = RocketService.from_rocket_model(
        RocketModel(**ROCKET_WITHOUT_MOTOR)
    )
    with pytest.raises(HTTPException) as exc:
        service.get_rocket_simulation()
    assert exc.value.status_code == 422
    assert 'motor' in exc.value.detail.lower()


def test_flight_without_motor_is_422():
    flight = FlightModel(
        environment={'latitude': 0.0, 'longitude': 0.0, 'elevation': 0.0},
        rocket=ROCKET_WITHOUT_MOTOR,
        rail_length=5.0,
    )
    with pytest.raises(HTTPException) as exc:
        FlightService.from_flight_model(flight)
    assert exc.value.status_code == 422
    assert 'motor' in exc.value.detail.lower()
