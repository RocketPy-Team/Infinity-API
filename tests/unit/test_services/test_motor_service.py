"""Tests for src.services.motor conversion helpers.

These exercise the translation from API Pydantic models to concrete
rocketpy objects. Unlike the route tests (which mock the controller),
these use the real rocketpy package so any mismatch between our
adapter and the rocketpy API surfaces immediately.
"""

import pytest
from rocketpy import (
    CylindricalTank,
    Fluid,
    Function,
    LevelBasedTank,
    LiquidMotor,
    MassBasedTank,
    MassFlowRateBasedTank,
    SphericalTank,
    TankGeometry,
    UllageBasedTank,
)

from src.models.motor import MotorModel
from src.models.sub.tanks import MotorTank, TankFluids, TankKinds
from src.services.motor import (
    MotorService,
    _build_rocketpy_fluid,
    _build_rocketpy_tank_geometry,
)


_LIQUID_CORE = {
    'thrust_source': [[0, 1000], [1, 500]],
    'burn_time': 1.0,
    'nozzle_radius': 0.05,
    'dry_mass': 5.0,
    'dry_inertia': [0.1, 0.1, 0.01],
    'center_of_dry_mass_position': 0.0,
    'motor_kind': 'LIQUID',
}


def _level_tank(geometry, liquid=None):
    return MotorTank(
        geometry=geometry,
        gas=TankFluids(name='N2', density=1.2),
        liquid=liquid or TankFluids(name='LOX', density=1141.0),
        flux_time=(0, 1.0),
        position=0.5,
        discretize=100,
        tank_kind=TankKinds.LEVEL,
        liquid_height=0.2,
    )


class TestGeometryAdapter:
    def test_custom_geometry_produces_generic_tank_geometry(self):
        tank = _level_tank(
            {
                'geometry_kind': 'custom',
                'geometry': [[(0.0, 1.0), 0.1]],
            }
        )
        built = _build_rocketpy_tank_geometry(tank.geometry)
        assert isinstance(built, TankGeometry)
        assert not isinstance(built, (CylindricalTank, SphericalTank))

    def test_cylindrical_geometry_produces_cylindrical_tank(self):
        tank = _level_tank(
            {
                'geometry_kind': 'cylindrical',
                'radius': 0.1,
                'height': 0.5,
                'spherical_caps': False,
            }
        )
        built = _build_rocketpy_tank_geometry(tank.geometry)
        assert isinstance(built, CylindricalTank)
        # height is the total cylindrical span
        assert built.height == pytest.approx(0.5)

    def test_spherical_geometry_produces_spherical_tank(self):
        tank = _level_tank(
            {'geometry_kind': 'spherical', 'radius': 0.2}
        )
        built = _build_rocketpy_tank_geometry(tank.geometry)
        assert isinstance(built, SphericalTank)


class TestFluidAdapter:
    def test_scalar_density_passes_through(self):
        fluid = _build_rocketpy_fluid(
            TankFluids(name='water', density=1000.0)
        )
        assert isinstance(fluid, Fluid)
        assert fluid.density == 1000.0

    def test_sampled_density_becomes_callable_function(self):
        fluid = _build_rocketpy_fluid(
            TankFluids(
                name='LOX',
                density=[[90.0, 1141.0], [120.0, 1091.0], [150.0, 1021.0]],
            )
        )
        assert isinstance(fluid, Fluid)
        # The 2-input density function interpolates correctly. Rocketpy
        # wraps our 1D callable so pressure is accepted but ignored.
        assert fluid.density_function.get_value(
            105.0, 1e5
        ) == pytest.approx(1116.0)
        assert fluid.density_function.get_value(
            135.0, 1e5
        ) == pytest.approx(1056.0)


class TestFromMotorModelLiquid:
    def test_mass_flow_tank_with_custom_geometry(self):
        # Sized so the propellant fits: radius 0.5 m, height 2 m →
        # tank volume ≈ 1.57 m³, which comfortably holds 10 kg of LOX
        # (~0.009 m³) plus 0.01 kg of N2 (~0.008 m³).
        motor_model = MotorModel(
            **_LIQUID_CORE,
            tanks=[
                MotorTank(
                    geometry={
                        'geometry_kind': 'custom',
                        'geometry': [[(-1.0, 1.0), 0.5]],
                    },
                    gas=TankFluids(name='N2', density=1.2),
                    liquid=TankFluids(name='LOX', density=1141.0),
                    flux_time=(0, 1.0),
                    position=0.5,
                    discretize=100,
                    tank_kind=TankKinds.MASS_FLOW,
                    initial_liquid_mass=10.0,
                    initial_gas_mass=0.01,
                    liquid_mass_flow_rate_in=0.0,
                    liquid_mass_flow_rate_out=5.0,
                    gas_mass_flow_rate_in=0.0,
                    gas_mass_flow_rate_out=0.0,
                ),
            ],
        )
        service = MotorService.from_motor_model(motor_model)
        assert isinstance(service.motor, LiquidMotor)
        tank = service.motor.positioned_tanks[0]['tank']
        assert isinstance(tank, MassFlowRateBasedTank)
        assert isinstance(tank.geometry, TankGeometry)

    def test_level_tank_with_cylindrical_geometry(self):
        motor_model = MotorModel(
            **_LIQUID_CORE,
            tanks=[
                _level_tank(
                    {
                        'geometry_kind': 'cylindrical',
                        'radius': 0.1,
                        'height': 0.5,
                    }
                )
            ],
        )
        service = MotorService.from_motor_model(motor_model)
        tank = service.motor.positioned_tanks[0]['tank']
        assert isinstance(tank, LevelBasedTank)
        assert isinstance(tank.geometry, CylindricalTank)

    def test_ullage_tank_with_spherical_geometry(self):
        motor_model = MotorModel(
            **_LIQUID_CORE,
            tanks=[
                MotorTank(
                    geometry={
                        'geometry_kind': 'spherical',
                        'radius': 0.2,
                    },
                    gas=TankFluids(name='N2', density=1.2),
                    liquid=TankFluids(name='LOX', density=1141.0),
                    flux_time=(0, 1.0),
                    position=0.5,
                    discretize=100,
                    tank_kind=TankKinds.ULLAGE,
                    ullage=0.01,
                )
            ],
        )
        service = MotorService.from_motor_model(motor_model)
        tank = service.motor.positioned_tanks[0]['tank']
        assert isinstance(tank, UllageBasedTank)
        assert isinstance(tank.geometry, SphericalTank)

    def test_mass_tank_keeps_sampled_density_as_function(self):
        motor_model = MotorModel(
            **_LIQUID_CORE,
            tanks=[
                MotorTank(
                    geometry={
                        'geometry_kind': 'cylindrical',
                        'radius': 0.1,
                        'height': 0.5,
                    },
                    gas=TankFluids(name='N2', density=1.2),
                    liquid=TankFluids(
                        name='LOX',
                        density=[
                            [90.0, 1141.0],
                            [120.0, 1091.0],
                            [150.0, 1021.0],
                        ],
                    ),
                    flux_time=(0, 1.0),
                    position=0.5,
                    discretize=100,
                    tank_kind=TankKinds.MASS,
                    liquid_mass=10.0,
                    gas_mass=0.001,
                ),
            ],
        )
        service = MotorService.from_motor_model(motor_model)
        tank = service.motor.positioned_tanks[0]['tank']
        assert isinstance(tank, MassBasedTank)
        # Liquid density survived as a Function wrapping our 1D sampler.
        assert isinstance(tank.liquid.density, Function)
        assert tank.liquid.density_function.get_value(
            105.0, 1e5
        ) == pytest.approx(1116.0)
        # Gas density stayed scalar.
        assert tank.gas.density == 1.2
