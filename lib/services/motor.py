from typing import Self
from rocketpy.motors.solid_motor import SolidMotor
from rocketpy.motors.liquid_motor import LiquidMotor
from rocketpy.motors.hybrid_motor import HybridMotor
from rocketpy.utilities import get_instance_attributes
from lib.models.motor import Motor, MotorKinds
from lib.views.motor import MotorSummary


class MotorService:

    @classmethod
    def from_motor_model(cls, motor: Motor) -> Self:
        """
        Get the rocketpy motor object.

        Returns:
            Mixin of rocketpy motor and MotorService
        """

        motor_core = {
            "thrust_source": (
                f"lib/data/engines/{motor.thrust_source.value}.eng"
            ),
            "burn_time": motor.burn_time,
            "nozzle_radius": motor.nozzle_radius,
            "dry_mass": motor.dry_mass,
            "dry_inertia": motor.dry_inertia,
            "center_of_dry_mass_position": motor.center_of_dry_mass_position,
        }

        match motor.motor_kind:
            case MotorKinds.LIQUID:
                rocketpy_motor = type(
                    "LiquidMotorMixin", (LiquidMotor, cls), {}
                )(**motor_core)
            case MotorKinds.HYBRID:
                rocketpy_motor = type(
                    "HybridMotorMixin", (HybridMotor, cls), {}
                )(
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
            case _:
                rocketpy_motor = type(
                    "SolidMotorMixin", (SolidMotor, cls), {}
                )(
                    **motor_core,
                    grain_number=motor.grain_number,
                    grain_density=motor.grain_density,
                    grain_outer_radius=motor.grain_outer_radius,
                    grain_initial_inner_radius=motor.grain_initial_inner_radius,
                    grain_initial_height=motor.grain_initial_height,
                    grains_center_of_mass_position=motor.grains_center_of_mass_position,
                    grain_separation=motor.grain_separation,
                    throat_radius=motor.throat_radius,
                    interpolation_method=motor.interpolation_method,
                )

        if motor.motor_kind != MotorKinds.SOLID:
            for tank in motor.tanks:
                rocketpy_motor.add_tank(tank.tank, tank.position)

        return rocketpy_motor

    def get_motor_summary(self) -> MotorSummary:
        """
        Get the summary of the motor.

        Returns:
            MotorSummary
        """
        attributes = get_instance_attributes(self)
        motor_summary = MotorSummary(**attributes)
        return motor_summary
