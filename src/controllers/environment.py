from src.controllers.interface import (
    ControllerBase,
    controller_exception_handler,
)
from src.views.environment import EnvironmentSimulation
from src.models.environment import EnvironmentModel
from src.services.environment import EnvironmentService


class EnvironmentController(ControllerBase):
    """
    Controller for the Environment model.

    Enables:
        - Simulation of a RocketPy Environment.
        - CRUD for Environment BaseApiModel.
    """

    def __init__(self):
        super().__init__(models=[EnvironmentModel])

    @controller_exception_handler
    async def get_rocketpy_environment_binary(
        self,
        env_id: str,
    ) -> bytes:
        """
        Get rocketpy.Environmnet dill binary.

        Args:
            env_id: str

        Returns:
            bytes

        Raises:
            HTTP 404 Not Found: If the env is not found in the database.
        """
        env = await self.get_environment_by_id(env_id)
        env_service = EnvironmentService.from_env_model(env.environment)
        return env_service.get_environment_binary()

    @controller_exception_handler
    async def get_environment_simulation(
        self, env_id: str
    ) -> EnvironmentSimulation:
        """
        Simulate a rocket environment.

        Args:
            env_id: str.

        Returns:
            EnvironmentSimulation

        Raises:
            HTTP 404 Not Found: If the env does not exist in the database.
        """
        env = await self.get_environment_by_id(env_id)
        env_service = EnvironmentService.from_env_model(env.environment)
        return env_service.get_environment_simulation()
