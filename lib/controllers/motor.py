from lib.controllers.interface import (
    ControllerInterface,
    controller_exception_handler,
)
from lib.views.motor import MotorSimulation
from lib.models.motor import MotorModel
from lib.services.motor import MotorService


class MotorController(ControllerInterface):
    """
    Controller for the motor model.

    Enables:
        - Simulation of a RocketPy Motor.
        - CRUD for Motor BaseApiModel.
    """

    def __init__(self):
        super().__init__(models=[MotorModel])

    @controller_exception_handler
    async def get_rocketpy_motor_binary(
        self,
        motor_id: str,
    ) -> bytes:
        """
        Get a rocketpy.Motor object as a dill binary.

        Args:
            motor_id: str

        Returns:
            bytes

        Raises:
            HTTP 404 Not Found: If the motor is not found in the database.
        """
        motor = await self.get_motor_by_id(motor_id)
        motor_service = MotorService.from_motor_model(motor)
        return motor_service.get_motor_binary()

    @controller_exception_handler
    async def get_motor_simulation(self, motor_id: str) -> MotorSimulation:
        """
        Simulate a rocketpy motor.

        Args:
            motor_id: str

        Returns:
            views.MotorSimulation

        Raises:
            HTTP 404 Not Found: If the motor does not exist in the database.
        """
        motor = await self.get_motor_by_id(motor_id)
        motor_service = MotorService.from_motor_model(motor)
        return motor_service.get_motor_simulation()
