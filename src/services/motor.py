from typing import Self

import dill

from rocketpy.motors.motor import GenericMotor, Motor as RocketPyMotor
from rocketpy.motors.solid_motor import SolidMotor
from rocketpy.motors.liquid_motor import LiquidMotor
from rocketpy.motors.hybrid_motor import HybridMotor
from rocketpy import (
    CylindricalTank,
    Fluid,
    Function,
    LevelBasedTank,
    MassBasedTank,
    MassFlowRateBasedTank,
    SphericalTank,
    TankGeometry,
    UllageBasedTank,
)

from fastapi import HTTPException, status

from src.models.sub.tanks import (
    CustomTankGeometry,
    CylindricalTankGeometry,
    SphericalTankGeometry,
    TankFluids,
    TankKinds,
)
from src.models.motor import MotorKinds, MotorModel
from src.views.motor import MotorSimulation
from src.utils import collect_attributes


def _build_rocketpy_tank_geometry(geometry):
    """Convert an API geometry model into a rocketpy geometry object.

    Dispatch mirrors the discriminated union in
    ``src.models.sub.tanks.TankGeometryInput``.
    """
    if isinstance(geometry, CylindricalTankGeometry):
        return CylindricalTank(
            radius=geometry.radius,
            height=geometry.height,
            spherical_caps=geometry.spherical_caps,
        )
    if isinstance(geometry, SphericalTankGeometry):
        return SphericalTank(radius=geometry.radius)
    if isinstance(geometry, CustomTankGeometry):
        return TankGeometry(geometry_dict=dict(geometry.geometry))
    raise ValueError(
        f"Unsupported tank geometry kind: {type(geometry).__name__}"
    )


def _build_rocketpy_fluid(fluids: TankFluids) -> Fluid:
    """Convert an API TankFluids into a rocketpy Fluid.

    Scalar density is passed through (Fluid stores it as a constant).
    Sampled density is converted to a 1D Temperature → Density Function
    and wrapped in a ``(T, P)`` callable because rocketpy's Fluid expects
    density to be a function of both temperature and pressure. Pressure
    is ignored here intentionally; only temperature-dependent density
    is supported in this iteration.
    """
    density = fluids.density
    if isinstance(density, list):
        temperature_to_density = Function(
            source=density,
            interpolation='linear',
            extrapolation='natural',
            inputs=['Temperature (K)'],
            outputs='Density (kg/m^3)',
        )

        def density_callable(temperature, pressure):  # noqa: ARG001
            # pylint: disable=unused-argument
            # Rocketpy's Fluid wraps this into a 2-input Function of
            # (T, P); pressure is accepted for signature compatibility
            # but intentionally ignored in this iteration.
            return temperature_to_density.get_value(temperature)

        return Fluid(name=fluids.name, density=density_callable)
    return Fluid(name=fluids.name, density=density)


class MotorService:
    _motor: RocketPyMotor

    def __init__(self, motor: RocketPyMotor = None):
        self._motor = motor

    @classmethod
    def from_motor_model(cls, motor: MotorModel) -> Self:
        """
        Get the rocketpy motor object.

        Returns:
            MotorService containing the rocketpy motor object.
        """

        reshape_thrust_curve = motor.reshape_thrust_curve
        if isinstance(reshape_thrust_curve, bool):
            reshape_thrust_curve = False
        elif isinstance(reshape_thrust_curve, list):
            reshape_thrust_curve = tuple(reshape_thrust_curve)

        motor_core = {
            "thrust_source": motor.thrust_source,
            "nozzle_radius": motor.nozzle_radius,
            "dry_mass": motor.dry_mass,
            "dry_inertia": motor.dry_inertia,
            "center_of_dry_mass_position": motor.center_of_dry_mass_position,
            "coordinate_system_orientation": motor.coordinate_system_orientation,
            "interpolation_method": motor.interpolation_method,
            "reshape_thrust_curve": reshape_thrust_curve,
        }
        # Only forward optional rocketpy args when the client supplied them.
        # Leaving them out lets rocketpy pick its own default (burn_time
        # auto-detected from thrust_source span; nozzle_position = 0).
        if motor.burn_time is not None:
            motor_core["burn_time"] = motor.burn_time
        if motor.nozzle_position is not None:
            motor_core["nozzle_position"] = motor.nozzle_position

        match MotorKinds(motor.motor_kind):
            case MotorKinds.LIQUID:
                rocketpy_motor = LiquidMotor(**motor_core)
            case MotorKinds.HYBRID:
                rocketpy_motor = HybridMotor(
                    **motor_core,
                    throat_radius=motor.throat_radius,
                    grain_number=motor.grain_number,
                    grain_density=motor.grain_density,
                    grain_outer_radius=motor.grain_outer_radius,
                    grain_initial_inner_radius=motor.grain_initial_inner_radius,
                    grain_initial_height=motor.grain_initial_height,
                    grain_separation=motor.grain_separation,
                    grains_center_of_mass_position=motor.grains_center_of_mass_position,
                )
            case MotorKinds.SOLID:
                grain_params = {
                    'grain_number': motor.grain_number,
                    'grain_density': motor.grain_density,
                    'grain_outer_radius': motor.grain_outer_radius,
                    'grain_initial_inner_radius': motor.grain_initial_inner_radius,
                    'grain_initial_height': motor.grain_initial_height,
                    'grain_separation': motor.grain_separation,
                    'grains_center_of_mass_position': motor.grains_center_of_mass_position,
                }

                missing = [
                    key for key, value in grain_params.items() if value is None
                ]
                if missing:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=(
                            "Solid motor requires grain configuration: missing "
                            + ', '.join(missing)
                        ),
                    )

                optional_params = {}
                if motor.throat_radius is not None:
                    optional_params['throat_radius'] = motor.throat_radius

                rocketpy_motor = SolidMotor(
                    **motor_core,
                    **grain_params,
                    **optional_params,
                )
            case _:
                # GenericMotor requires burn_time even though it's optional
                # for the other motor kinds — surface the constraint at the
                # API boundary instead of letting rocketpy raise a
                # confusing stack trace deeper in construction.
                if motor.burn_time is None:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="burn_time is required for generic motors.",
                    )
                # nozzle_position is already forwarded via motor_core when
                # the client supplied it; GenericMotor's own default (0)
                # applies otherwise.
                rocketpy_motor = GenericMotor(
                    **motor_core,
                    chamber_radius=motor.chamber_radius,
                    chamber_height=motor.chamber_height,
                    chamber_position=motor.chamber_position,
                    propellant_initial_mass=motor.propellant_initial_mass,
                )

        if motor.motor_kind not in (MotorKinds.SOLID, MotorKinds.GENERIC):
            for tank in motor.tanks or []:
                tank_core = {
                    "name": tank.name,
                    "geometry": _build_rocketpy_tank_geometry(tank.geometry),
                    "flux_time": tank.flux_time,
                    "gas": _build_rocketpy_fluid(tank.gas),
                    "liquid": _build_rocketpy_fluid(tank.liquid),
                    "discretize": tank.discretize,
                }

                match tank.tank_kind:
                    case TankKinds.LEVEL:
                        rocketpy_tank = LevelBasedTank(
                            **tank_core, liquid_height=tank.liquid_height
                        )
                    case TankKinds.MASS:
                        rocketpy_tank = MassBasedTank(
                            **tank_core,
                            liquid_mass=tank.liquid_mass,
                            gas_mass=tank.gas_mass,
                        )
                    case TankKinds.MASS_FLOW:
                        rocketpy_tank = MassFlowRateBasedTank(
                            **tank_core,
                            gas_mass_flow_rate_in=tank.gas_mass_flow_rate_in,
                            gas_mass_flow_rate_out=tank.gas_mass_flow_rate_out,
                            liquid_mass_flow_rate_in=tank.liquid_mass_flow_rate_in,
                            liquid_mass_flow_rate_out=tank.liquid_mass_flow_rate_out,
                            initial_liquid_mass=tank.initial_liquid_mass,
                            initial_gas_mass=tank.initial_gas_mass,
                        )
                    case TankKinds.ULLAGE:
                        rocketpy_tank = UllageBasedTank(
                            **tank_core, ullage=tank.ullage
                        )
                rocketpy_motor.add_tank(rocketpy_tank, tank.position)

        return cls(motor=rocketpy_motor)

    @property
    def motor(self) -> RocketPyMotor:
        return self._motor

    @motor.setter
    def motor(self, motor: RocketPyMotor):
        self._motor = motor

    def get_motor_simulation(self) -> MotorSimulation:
        """
        Get the simulation of the motor.

        Returns:
            MotorSimulation
        """
        encoded_attributes = collect_attributes(
            self.motor,
            [MotorSimulation],
        )
        motor_simulation = MotorSimulation(**encoded_attributes)
        return motor_simulation

    def get_motor_binary(self) -> bytes:
        """
        Get the binary representation of the motor.

        Returns:
            bytes
        """
        return dill.dumps(self.motor)
