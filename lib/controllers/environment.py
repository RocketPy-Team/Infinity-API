from lib.controllers.interface import (
    ControllerInterface,
    controller_exception_handler,
)
from lib.views.environment import EnvSummary
from lib.models.environment import EnvironmentModel
from lib.services.environment import EnvironmentService


class EnvironmentController(ControllerInterface):
    """
    Controller for the Environment model.

    Enables:
        - Simulation of a RocketPy Environment.
        - CRUD for Environment BaseApiModel.
    """

    def __init__(self):
        super().__init__(models=[EnvironmentModel])

    @controller_exception_handler
    async def get_rocketpy_env_binary(
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
        env = await self.get_env_by_id(env_id)
        env_service = EnvironmentService.from_env_model(env)
        return env_service.get_env_binary()

    @controller_exception_handler
    async def simulate_env(
        self, env_id: str
    ) -> EnvSummary:
        """
        Simulate a rocket environment.

        Args:
            env_id: str.

        Returns:
            EnvSummary

        Raises:
            HTTP 404 Not Found: If the env does not exist in the database.
        """
        env = await self.get_env_by_id(env_id)
        env_service = EnvironmentService.from_env_model(env)
        return env_service.get_env_summary()
