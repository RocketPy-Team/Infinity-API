from src.controllers.interface import (
    ControllerBase,
    controller_exception_handler,
)
from src.views.motor import MotorSimulation, MotorList, MotorView
from src.models.motor import MotorModel
from src.services.motor import MotorService
from src.repositories.interface import RepositoryInterface


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
    async def list_motors(self, skip: int, limit: int) -> MotorList:
        model_repo = RepositoryInterface.get_model_repo(MotorModel)
        async with model_repo() as repo:
            total, items = await repo.list_motors(skip=skip, limit=limit)
            return MotorList(
                items=[
                    MotorView(**item.model_dump(), motor_id=item.get_id())
                    for item in items
                ],
                total=total,
                skip=skip,
                limit=limit,
            )
