"""Tests for src.services.rocket adapter behaviour that the RocketPy example
corpus (regression-suite/designs) exposed."""

import math

import pytest

from src.models.rocket import RocketModel
from src.services.rocket import RocketService, _drag_curve_function


def _rocket_model(**overrides):
    base = {
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
        'power_off_drag': [[0, 0.5], [0.5, 0.5], [1.0, 0.6]],
        'power_on_drag': [[0, 0.5], [0.5, 0.5], [1.0, 0.6]],
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
                'rocket_radius': 0.1,
            }
        ],
    }
    base.update(overrides)
    return RocketModel(**base)


class TestDragCurves:
    # The notebooks hand rocketpy a CSV *path*, which goes through
    # Rocket.__load_rocket_drag_csv (linear interpolation, constant
    # extrapolation, duplicate Mach rows tolerated). Infinity's wire format
    # forces an inline list, which rocketpy routes through Function(list)
    # with the default *spline* interpolation — duplicate Mach rows make the
    # spline solve NaN and the whole rocket is rejected ("Invalid list/tuple
    # format for Drag Coefficient with Power Off"). Five of the official
    # example drag CSVs contain duplicate Mach rows, so the adapter must
    # mirror the CSV loader.

    def test_duplicate_mach_rows_are_collapsed_keeping_first(self):
        func = _drag_curve_function(
            [[0.0, 0.5], [0.5, 0.55], [0.5, 0.9], [1.0, 0.6]],
            'Drag Coefficient with Power Off',
        )
        assert func(0.5) == pytest.approx(0.55)
        assert math.isfinite(func(0.25))

    def test_interpolation_is_linear_with_constant_extrapolation(self):
        func = _drag_curve_function(
            [[0.0, 0.4], [1.0, 0.6]], 'Drag Coefficient with Power On'
        )
        assert func(0.5) == pytest.approx(0.5)
        assert func(5.0) == pytest.approx(0.6)
        assert func(-1.0) == pytest.approx(0.4)

    def test_rocket_with_duplicate_mach_rows_builds(self):
        curve = [[0.0, 0.5], [0.3, 0.5], [0.3, 0.5], [0.8, 0.52], [1.0, 0.6]]
        model = _rocket_model(power_off_drag=curve, power_on_drag=curve)
        service = RocketService.from_rocket_model(model)
        drag = service.rocket.power_off_drag
        # rocketpy keeps a Mach-only curve 1-D and lifts a 7-D one as is.
        args = (0.9,) if drag.__dom_dim__ == 1 else (0, 0, 0.9, 1e6, 0, 0, 0)
        cd = drag(*args)
        assert math.isfinite(cd)
        assert cd == pytest.approx(0.56)

    def test_unsorted_rows_are_sorted_by_mach(self):
        func = _drag_curve_function(
            [[1.0, 0.6], [0.0, 0.4]], 'Drag Coefficient with Power Off'
        )
        assert func(0.5) == pytest.approx(0.5)
