from typing import Union
from fastapi import HTTPException, status
from rocketpy.motors.solid_motor import SolidMotor
from rocketpy.motors.liquid_motor import LiquidMotor
from rocketpy.motors.hybrid_motor import HybridMotor
import jsonpickle

from lib.models.motor import Motor, MotorKinds
from lib.repositories.motor import MotorRepository
from lib.views.motor import (
    MotorSummary,
    MotorData,
    MotorCreated,
    MotorUpdated,
    MotorDeleted,
    MotorPickle,
)


class MotorController:
    """
    Controller for the motor model.

    Init Attributes:
        motor (models.Motor): Motor model object.

    Enables:
        - Create a rocketpy.Motor object from a Motor model object.
    """

    def __init__(self, motor: Motor, motor_kind):
        self.guard(motor, motor_kind)
        motor_core = {
            "thrust_source": f"lib/data/engines/{motor.thrust_source.value}.eng",
            "burn_time": motor.burn_time,
            "nozzle_radius": motor.nozzle_radius,
            "dry_mass": motor.dry_mass,
            "dry_inertia": motor.dry_inertia,
            "center_of_dry_mass_position": motor.center_of_dry_mass_position,
        }

        match motor_kind:
            case MotorKinds.liquid:
                rocketpy_motor = LiquidMotor(**motor_core)
            case MotorKinds.hybrid:
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
            case _:
                rocketpy_motor = SolidMotor(
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

        if motor_kind != MotorKinds.solid:
            for tank in motor.tanks:
                rocketpy_motor.add_tank(tank.tank, tank.position)

        self.motor_kind = motor_kind  # tracks motor kind state
        self.rocketpy_motor = rocketpy_motor
        self.motor = motor

    def guard(self, motor: Motor, motor_kind):
        if motor_kind != MotorKinds.solid and motor.tanks is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Tanks must be provided for liquid and hybrid motors.",
            )

    async def create_motor(self) -> "Union[MotorCreated, HTTPException]":
        """
        Create a motor in the database.

        Returns:
            MotorCreated: motor id.
        """
        motor = MotorRepository(motor=self.motor)
        successfully_created_motor = await motor.create_motor(
            motor_kind=self.motor_kind
        )
        if not successfully_created_motor:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create motor.",
            )

        return MotorCreated(motor_id=str(motor.motor_id))

    @staticmethod
    async def get_motor(motor_id: int) -> "Union[Motor, HTTPException]":
        """
        Get a motor from the database.

        Args:
            motor_id (int): Motor id.

        Returns:
            Motor model object

        Raises:
            HTTP 404 Not Found: If the motor is not found in the database.
        """
        successfully_read_motor = await MotorRepository(motor_id=motor_id).get_motor()
        if not successfully_read_motor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Motor not found."
            )

        return successfully_read_motor

    @staticmethod
    async def get_rocketpy_motor(motor_id: int) -> "Union[MotorPickle, HTTPException]":
        """
        Get a rocketpy motor object encoded as jsonpickle string from the database.

        Args:
            motor_id (int): Motor id.

        Returns:
            str: jsonpickle string of the rocketpy motor.

        Raises:
            HTTP 404 Not Found: If the motor is not found in the database.
        """
        successfully_read_motor = await MotorRepository(motor_id=motor_id).get_motor()
        if not successfully_read_motor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Motor not found."
            )

        successfully_read_rocketpy_motor = MotorController(
            motor=successfully_read_motor,
            motor_kind=MotorKinds(successfully_read_motor._motor_kind),
        ).rocketpy_motor

        return MotorPickle(
            jsonpickle_rocketpy_motor=jsonpickle.encode(
                successfully_read_rocketpy_motor
            )
        )

    async def update_motor(self, motor_id: int) -> "Union[MotorUpdated, HTTPException]":
        """
        Update a motor in the database.

        Args:
            motor_id (int): Motor id.

        Returns:
            MotorUpdated: motor id and message.

        Raises:
            HTTP 404 Not Found: If the motor is not found in the database.
        """
        successfully_read_motor = await MotorRepository(motor_id=motor_id).get_motor()
        if not successfully_read_motor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Motor not found."
            )

        successfully_updated_motor = await MotorRepository(
            motor=self.motor, motor_id=motor_id
        ).update_motor(motor_kind=self.motor_kind)
        if not successfully_updated_motor:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update motor.",
            )

        return MotorUpdated(new_motor_id=str(successfully_updated_motor))

    @staticmethod
    async def delete_motor(motor_id: int) -> "Union[MotorDeleted, HTTPException]":
        """
        Delete a motor from the database.

        Args:
            motor_id (int): motor id.

        Returns:
            MotorDeleted: motor id and message.

        Raises:
            HTTP 404 Not Found: If the motor is not found in the database.
        """
        successfully_read_motor = await MotorRepository(motor_id=motor_id).get_motor()
        if not successfully_read_motor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Motor not found."
            )

        successfully_deleted_motor = await MotorRepository(
            motor_id=motor_id
        ).delete_motor()
        if not successfully_deleted_motor:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete motor.",
            )

        return MotorDeleted(deleted_motor_id=str(motor_id))

    @staticmethod
    async def simulate(motor_id: int) -> "Union[MotorSummary, HTTPException]":
        """
        Simulate a rocketpy motor.

        Args:
            motor_id (int): Motor id.

        Returns:
            motor summary view.

        Raises:
            HTTP 404 Not Found: If the motor does not exist in the database.
        """
        successfully_read_motor = await MotorRepository(motor_id=motor_id).get_motor()
        if not successfully_read_motor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Motor not found."
            )

        try:
            motor = MotorController(
                motor=successfully_read_motor,
                motor_kind=MotorKinds(successfully_read_motor._motor_kind),
            ).rocketpy_motor
            motor_simulation_numbers = MotorData(
                total_burning_time="Total Burning Time: "
                + str(motor.burn_out_time)
                + " s",
                total_propellant_mass="Total Propellant Mass: "
                + "{:.3f}".format(motor.propellant_initial_mass)
                + " kg",
                average_propellant_exhaust_velocity="Average Propellant Exhaust Velocity: "
                + "{:.3f}".format(motor.exhaust_velocity.average(*motor.burn_time))
                + " m/s",
                average_thrust="Average Thrust: "
                + "{:.3f}".format(motor.average_thrust)
                + " N",
                maximum_thrust="Maximum Thrust: "
                + str(motor.max_thrust)
                + " N at "
                + str(motor.max_thrust_time)
                + " s after ignition.",
                total_impulse="Total Impulse: "
                + "{:.3f}".format(motor.total_impulse)
                + " Ns\n",
            )
            # motor_simulation_plots = MotorPlots(
            #    motor.thrust.plot(lower=lower_limit, upper=upper_limit)
            # )
            motor_summary = MotorSummary(
                motor_data=motor_simulation_numbers
            )  # , plots=motor_simulation_plots )
            return motor_summary
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to simulate motor: {e}",
            ) from e
