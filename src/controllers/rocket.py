from fastapi import HTTPException, status

from src.controllers.interface import (
    ControllerBase,
    controller_exception_handler,
)
from src.views.rocket import RocketSimulation, RocketCreated
from src.models.motor import MotorModel
from src.models.rocket import (
    RocketModel,
    RocketWithMotorReferenceRequest,
)
from src.repositories.interface import RepositoryInterface
from src.services.rocket import RocketService


class RocketController(ControllerBase):
    """
    Controller for the Rocket model.

    Enables:
       - Simulation of a RocketPy Rocket.
       - CRUD for Rocket BaseApiModel.
    """

    def __init__(self):
        super().__init__(models=[RocketModel])

    async def _load_motor(self, motor_id: str) -> MotorModel:
        repo_cls = RepositoryInterface.get_model_repo(MotorModel)
        async with repo_cls() as repo:
            motor = await repo.read_motor_by_id(motor_id)
        if motor is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Motor not found",
            )
        return motor

    @controller_exception_handler
    async def create_rocket_from_motor_reference(
        self, payload: RocketWithMotorReferenceRequest
    ) -> RocketCreated:
        motor = await self._load_motor(payload.motor_id)
        rocket_model = payload.rocket.assemble(motor)
        return await self.post_rocket(rocket_model)

    @controller_exception_handler
    async def update_rocket_from_motor_reference(
        self,
        rocket_id: str,
        payload: RocketWithMotorReferenceRequest,
    ) -> None:
        motor = await self._load_motor(payload.motor_id)
        rocket_model = payload.rocket.assemble(motor)
        rocket_model.set_id(rocket_id)
        await self.put_rocket_by_id(rocket_id, rocket_model)
        return

    @controller_exception_handler
    async def get_rocketpy_rocket_binary(self, rocket_id: str) -> bytes:
        """
        Get a rocketpy.Rocket object as dill binary.

        Args:
            rocket_id: str

        Returns:
            bytes

        Raises:
            HTTP 404 Not Found: If the rocket is not found in the database.
        """
        rocket = await self.get_rocket_by_id(rocket_id)
        rocket_service = RocketService.from_rocket_model(rocket.rocket)
        return rocket_service.get_rocket_binary()

    @controller_exception_handler
    async def get_rocket_simulation(
        self,
        rocket_id: str,
    ) -> RocketSimulation:
        """
        Simulate a rocketpy rocket.

        Args:
            rocket_id: str

        Returns:
            views.RocketSimulation

        Raises:
            HTTP 404 Not Found: If the rocket does not exist in the database.
        """
        rocket = await self.get_rocket_by_id(rocket_id)
        rocket_service = RocketService.from_rocket_model(rocket.rocket)
        return rocket_service.get_rocket_simulation()
