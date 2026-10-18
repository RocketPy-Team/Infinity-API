"""FlightModel field typing against rocketpy's Flight signature."""

from src.models.flight import FlightModel


def _flight(**overrides):
    base = {
        'environment': {'latitude': 0.0, 'longitude': 0.0, 'elevation': 0.0},
        'rocket': {
            'motor': {
                'thrust_source': [[0, 1000], [1, 500]],
                'burn_time': 1.0,
                'nozzle_radius': 0.05,
                'dry_mass': 1.0,
                'center_of_dry_mass_position': 0.0,
                'motor_kind': 'GENERIC',
                'chamber_radius': 0.05,
                'chamber_height': 0.5,
                'chamber_position': 0.25,
                'propellant_initial_mass': 1.0,
            },
            'radius': 0.1,
            'mass': 10.0,
            'motor_position': 0.0,
            'center_of_mass_without_motor': 0.0,
            'nose': {
                'name': 'Nose',
                'length': 0.5,
                'kind': 'vonKarman',
                'position': 1.0,
                'base_radius': 0.1,
                'rocket_radius': 0.1,
            },
            'fins': [
                {
                    'fins_kind': 'trapezoidal',
                    'name': 'Fins',
                    'n': 4,
                    'root_chord': 0.2,
                    'span': 0.1,
                    'position': -0.5,
                    'tip_chord': 0.1,
                }
            ],
        },
    }
    base.update(overrides)
    return FlightModel(**base)


def test_max_time_accepts_fractional_seconds():
    # rocketpy.Flight(max_time=...) is a float; the lince example uses
    # 399.35159. Typing it as int rejected the notebook with
    # "Input should be a valid integer, got a number with a fractional part".
    flight = _flight(max_time=399.35159)
    assert flight.max_time == 399.35159
    assert flight.get_additional_parameters()['max_time'] == 399.35159


def test_min_time_step_accepts_fractional_seconds():
    flight = _flight(min_time_step=0.001)
    assert flight.min_time_step == 0.001
