from fastapi import Response, status
from typing import Any, Dict, Union
from rocketpy.motors.solid_motor import SolidMotor
import jsonpickle

from lib.models.motor import Motor
from lib.repositories.motor import MotorRepository
from lib.views.motor import MotorSummary, MotorData, MotorCreated, MotorUpdated, MotorDeleted, MotorPickle

class MotorController():
    """
    Controller for the motor model.

    Init Attributes:
        motor (models.Motor): Motor model object.

    Enables:
        - Create a rocketpy.Motor object from a Motor model object.
    """
    def __init__(self, motor: Motor):
        rocketpy_motor = SolidMotor(
                burn_time=motor.burn_time,
                grain_number=motor.grain_number,
                grain_density=motor.grain_density,
                grain_outer_radius=motor.grain_outer_radius,
                grain_initial_inner_radius=motor.grain_initial_inner_radius,
                grain_initial_height=motor.grain_initial_height,
                grains_center_of_mass_position=-motor.grains_center_of_mass_position,
                thrust_source=motor.thrust_source,
                grain_separation=motor.grain_separation,
                nozzle_radius=motor.nozzle_radius,
                dry_mass=motor.dry_mass,
                center_of_dry_mass_position=motor.center_of_dry_mass_position,
                dry_inertia=motor.dry_inertia,
                throat_radius=motor.throat_radius,
                interpolation_method=motor.interpolation_method
        )
        self.rocketpy_motor = rocketpy_motor
        self.motor = motor

    async def create_motor(self) -> "Dict[str, str]":
        """
        Create a motor in the database.

        Returns:
            Dict[str, str]: motor id.
        """
        motor = MotorRepository(motor=self.motor)
        successfully_created_motor = await motor.create_motor()
        if successfully_created_motor:
            return MotorCreated(motor_id=str(motor.motor_id))
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    async def get_motor(motor_id: int) -> "Union[Motor, Response]":
        """
        Get a motor from the database.

        Args:
            motor_id (int): Motor id.

        Returns:
            Motor model object

        Raises:
            HTTP 404 Not Found: If the motor is not found in the database.
        """
        successfully_read_motor = \
            await MotorRepository(motor_id=motor_id).get_motor()
        if not successfully_read_motor:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
        return successfully_read_motor

    @staticmethod
    async def get_rocketpy_motor(motor_id: int) -> "Union[Dict[str, Any], Response]":
        """
        Get a rocketpy motor object encoded as jsonpickle string from the database.

        Args:
            motor_id (int): Motor id.

        Returns:
            str: jsonpickle string of the rocketpy motor.

        Raises:
            HTTP 404 Not Found: If the motor is not found in the database.
        """
        successfully_read_motor = \
            await MotorRepository(motor_id=motor_id).get_motor()
        if not successfully_read_motor:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        successfully_read_rocketpy_motor = \
            MotorController( successfully_read_motor ).rocketpy_motor

        return MotorPickle(jsonpickle_rocketpy_motor=jsonpickle.encode(successfully_read_rocketpy_motor))

    async def update_motor(self, motor_id: int) -> "Union[Dict[str, Any], Response]":
        """
        Update a motor in the database.

        Args:
            motor_id (int): Motor id.

        Returns:
            Dict[str, Any]: motor id and message.

        Raises:
            HTTP 404 Not Found: If the motor is not found in the database.
        """
        successfully_read_motor = \
            await MotorRepository(motor_id=motor_id).get_motor()
        if not successfully_read_motor:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        successfully_updated_motor = \
            await MotorRepository(motor=self.motor, motor_id=motor_id).update_motor()

        if successfully_updated_motor:
            return MotorUpdated(new_motor_id=str(successfully_updated_motor))
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    async def delete_motor(motor_id: int) -> "Union[Dict[str, str], Response]":
        """
        Delete a motor from the database.

        Args:
            motor_id (int): motor id.

        Returns:
            Dict[str, str]: motor id and message.

        Raises:
            HTTP 404 Not Found: If the motor is not found in the database.
        """
        successfully_read_motor = \
            await MotorRepository(motor_id=motor_id).get_motor()
        if not successfully_read_motor:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        successfully_deleted_motor = \
            await MotorRepository(motor_id=motor_id).delete_motor()
        if successfully_deleted_motor:
            return MotorDeleted(deleted_motor_id=str(motor_id))
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    async def simulate(motor_id: int) -> "Union[MotorSummary, Response]":
        """
        Simulate a rocketpy motor.

        Args:
            motor_id (int): Motor id.

        Returns:
            motor summary view.

        Raises:
            HTTP 404 Not Found: If the motor does not exist in the database.
        """
        successfully_read_motor = \
            await MotorRepository(motor_id=motor_id).get_motor()
        if not successfully_read_motor:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        motor = MotorController(successfully_read_motor).rocketpy_motor
        motor_simulation_numbers = MotorData(
            total_burning_time="Total Burning Time: " + str(motor.burn_out_time) + " s",

            total_propellant_mass="Total Propellant Mass: "
            + "{:.3f}".format(motor.propellant_initial_mass)
            + " kg",

            average_propellant_exhaust_velocity="Average Propellant Exhaust Velocity: "
            + "{:.3f}".format(
                motor.exhaust_velocity.average(*motor.burn_time)
            )
            + " m/s",

            average_thrust="Average Thrust: " + "{:.3f}".format(motor.average_thrust) + " N",

            maximum_thrust="Maximum Thrust: "
            + str(motor.max_thrust)
            + " N at "
            + str(motor.max_thrust_time)
            + " s after ignition.",

            total_impulse="Total Impulse: " + "{:.3f}".format(motor.total_impulse) + " Ns\n"
        )
        #motor_simulation_plots = MotorPlots(
        #    motor.thrust.plot(lower=lower_limit, upper=upper_limit)
        #)

        motor_summary = MotorSummary( motor_data = motor_simulation_numbers ) #, plots=motor_simulation_plots )
        return motor_summary
