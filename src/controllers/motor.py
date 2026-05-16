from src.controllers.interface import (
    ControllerBase,
    controller_exception_handler,
)
from src.views.motor import MotorSimulation, MotorDrawingGeometryView
from src.models.motor import MotorModel
from src.services.motor import MotorService


class MotorController(ControllerBase):
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
        motor_service = MotorService.from_motor_model(motor.motor)
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
        motor_service = MotorService.from_motor_model(motor.motor)
        return motor_service.get_motor_simulation()

    @controller_exception_handler
    async def get_motor_drawing_geometry(
        self, motor_id: str
    ) -> MotorDrawingGeometryView:
        """
        Build the motor-only drawing-geometry payload for a persisted motor.

        Renders the motor at its own coordinate origin (motor_position=0,
        parent_csys=1) so the playground can show a motor in isolation.

        Args:
            motor_id: str

        Returns:
            views.MotorDrawingGeometryView

        Raises:
            HTTP 404 Not Found: If the motor does not exist in the database.
            HTTP 422: If the motor has no drawable geometry.
        """
        motor = await self.get_motor_by_id(motor_id)
        motor_service = MotorService.from_motor_model(motor.motor)
        return motor_service.get_drawing_geometry()
