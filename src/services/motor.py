from typing import Self

import dill

from rocketpy.motors.motor import GenericMotor, Motor as RocketPyMotor
from rocketpy.motors.solid_motor import SolidMotor
from rocketpy.motors.liquid_motor import LiquidMotor
from rocketpy.motors.hybrid_motor import HybridMotor
from rocketpy import (
    LevelBasedTank,
    MassBasedTank,
    MassFlowRateBasedTank,
    UllageBasedTank,
    TankGeometry,
)

from fastapi import HTTPException, status

from src.models.sub.tanks import TankKinds
from src.models.motor import MotorKinds, MotorModel
from src.views.motor import MotorSimulation
from src.utils import collect_attributes


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
            "burn_time": motor.burn_time,
            "nozzle_radius": motor.nozzle_radius,
            "dry_mass": motor.dry_mass,
            "dry_inertia": motor.dry_inertia,
            "center_of_dry_mass_position": motor.center_of_dry_mass_position,
            "coordinate_system_orientation": motor.coordinate_system_orientation,
            "interpolation_method": motor.interpolation_method,
            "reshape_thrust_curve": reshape_thrust_curve,
        }

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
                rocketpy_motor = GenericMotor(
                    **motor_core,
                    chamber_radius=motor.chamber_radius,
                    chamber_height=motor.chamber_height,
                    chamber_position=motor.chamber_position,
                    propellant_initial_mass=motor.propellant_initial_mass,
                    nozzle_position=motor.nozzle_position,
                )

        if motor.motor_kind not in (MotorKinds.SOLID, MotorKinds.GENERIC):
            for tank in motor.tanks or []:
                tank_core = {
                    "name": tank.name,
                    "geometry": TankGeometry(
                        geometry_dict=dict(tank.geometry)
                    ),
                    "flux_time": tank.flux_time,
                    "gas": tank.gas,
                    "liquid": tank.liquid,
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
