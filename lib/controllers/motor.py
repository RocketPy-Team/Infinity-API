from lib.models.motor import Motor
from lib.repositories.motor import MotorRepository

from rocketpy import SolidMotor

from fastapi import Response, status
from typing import Any, Dict, Union

import jsonpickle

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
                burnOut=motor.burnOut,
                grainNumber=motor.grainNumber,
                grainDensity=motor.grainDensity,
                grainOuterRadius=motor.grainOuterRadius,
                grainInitialInnerRadius=motor.grainInitialInnerRadius,
                grainInitialHeight=motor.grainInitialHeight,
                grainsCenterOfMassPosition=-motor.grainsCenterOfMassPosition,
                thrustSource=motor.thrustSource
        )
        rocketpy_motor.grainSeparation = motor.grainSeparation
        rocketpy_motor.nozzleRadius = motor.nozzleRadius
        rocketpy_motor.throatRadius = motor.throatRadius
        rocketpy_motor.interpolationMethod = motor.interpolationMethod
        self.rocketpy_motor = rocketpy_motor
        self.motor = motor

    def create_motor(self) -> "Dict[str, str]":
        """
        Create a motor in the database.

        Returns:
            Dict[str, str]: motor id.
        """
        motor = MotorRepository(motor=self.motor)
        successfully_created_motor = motor.create_motor()
        if successfully_created_motor: 
            return { "message": "motor created", "motor_id": motor.motor_id }
        else:
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_motor(motor_id: int) -> "Union[Motor, Response]":
        """
        Get a motor from the database.

        Args:
            motor_id (int): Motor id.

        Returns:
            Motor model object

        Raises:
            HTTP 404 Not Found: If the motor is not found in the database. 
        """
        successfully_read_motor = MotorRepository(motor_id=motor_id).get_motor()
        if not successfully_read_motor:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
        return successfully_read_motor

    def get_rocketpy_motor(motor_id: int) -> "Union[Dict[str, Any], Response]":
        """
        Get a rocketpy motor object encoded as jsonpickle string from the database.

        Args:
            motor_id (int): Motor id.

        Returns:
            str: jsonpickle string of the rocketpy motor.

        Raises:
            HTTP 404 Not Found: If the motor is not found in the database.
        """
        successfully_read_motor = MotorRepository(motor_id=motor_id).get_motor()
        if not successfully_read_motor:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        successfully_read_rocketpy_motor  = MotorController( successfully_read_motor ).rocketpy_motor

        return { "jsonpickle_rocketpy_motor": jsonpickle.encode(successfully_read_rocketpy_motor) }

           
    def update_motor(self, motor_id: int) -> "Union[Dict[str, Any], Response]":
        """
        Update a motor in the database.

        Args:
            motor_id (int): Motor id.

        Returns:
            Dict[str, Any]: motor id and message.

        Raises:
            HTTP 404 Not Found: If the motor is not found in the database.
        """
        successfully_read_motor = MotorRepository(motor_id=motor_id).get_motor()
        if not successfully_read_motor:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        successfully_updated_motor = \
                MotorRepository(motor=self.motor, motor_id=motor_id).update_motor()

        if successfully_updated_motor:
            return { 
                    "message": "motor updated successfully", 
                    "new_motor_id": successfully_updated_motor
            }
        else:
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete_motor(motor_id: int) -> "Union[Dict[str, str], Response]":
        """
        Delete a motor from the database.

        Args:
            motor_id (int): motor id.

        Returns:
            Dict[str, str]: motor id and message.

        Raises:
            HTTP 404 Not Found: If the motor is not found in the database.
        """
        successfully_read_motor = MotorRepository(motor_id=motor_id).get_motor()
        if not successfully_read_motor:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        successfully_deleted_motor = MotorRepository(motor_id=motor_id).delete_motor()
        if successfully_deleted_motor: 
            return {"motor_id": motor_id, "message": "motor deleted successfully"}
        else:
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def simulate(motor_id: int) -> "Union[MotorSummary, Response]":
        """
        Simulate a rocketpy motor.

        Args:
            motor_id (int): Motor id.

        Returns:
            motor summary view.

        Raises:
            HTTP 404 Not Found: If the motor does not exist in the database.
        """
        successfully_read_motor = MotorRepository(motor_id=motor_id).get_motor()
        if not successfully_read_motor:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        #motor = MotorController(successfully_read_motor).rocketpy_motor
        #motor_simulation_numbers = motorData.parse_obj(motor.allInfoReturned())
        #motor_simulation_plots = motorPlots.parse_obj(motor.allPlotInfoReturned())

        #motor_summary = MotorSummary( data=motor_simulation_numbers, plots=motor_simulation_plots )

        #return motor_summary
        pass

