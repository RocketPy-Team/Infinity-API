from src.controllers.interface import (
    ControllerBase,
    controller_exception_handler,
)
from src.views.rocket import RocketSimulation
from src.models.rocket import RocketModel
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
        rocket_retrieved = await self.get_rocket_by_id(rocket_id)
        rocket_service = RocketService.from_rocket_model(
            rocket_retrieved.rocket
        )
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
        rocket_retrieved = await self.get_rocket_by_id(rocket_id)
        rocket_service = RocketService.from_rocket_model(
            rocket_retrieved.rocket
        )
        return rocket_service.get_rocket_simulation()
