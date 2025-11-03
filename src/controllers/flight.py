from fastapi import HTTPException, status

from src.controllers.interface import (
    ControllerBase,
    controller_exception_handler,
)
from src.views.flight import FlightSimulation, FlightCreated
from src.models.flight import (
    FlightModel,
    FlightWithReferencesRequest,
)
from src.models.environment import EnvironmentModel
from src.models.rocket import RocketModel
from src.repositories.interface import RepositoryInterface
from src.services.flight import FlightService


class FlightController(ControllerBase):
    """
    Controller for the Flight model.

    Enables:
        - Simulation of a RocketPy Flight.
        - CRUD for Flight BaseApiModel.
    """

    def __init__(self):
        super().__init__(models=[FlightModel])

    async def _load_environment(self, environment_id: str) -> EnvironmentModel:
        repo_cls = RepositoryInterface.get_model_repo(EnvironmentModel)
        async with repo_cls() as repo:
            environment = await repo.read_environment_by_id(environment_id)
        if environment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Environment not found",
            )
        return environment

    async def _load_rocket(self, rocket_id: str) -> RocketModel:
        repo_cls = RepositoryInterface.get_model_repo(RocketModel)
        async with repo_cls() as repo:
            rocket = await repo.read_rocket_by_id(rocket_id)
        if rocket is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rocket not found",
            )
        return rocket

    @controller_exception_handler
    async def create_flight_from_references(
        self, payload: FlightWithReferencesRequest
    ) -> FlightCreated:
        environment = await self._load_environment(payload.environment_id)
        rocket = await self._load_rocket(payload.rocket_id)
        flight_model = payload.flight.assemble(
            environment=environment,
            rocket=rocket,
        )
        return await self.post_flight(flight_model)

    @controller_exception_handler
    async def update_flight_from_references(
        self,
        flight_id: str,
        payload: FlightWithReferencesRequest,
    ) -> None:
        environment = await self._load_environment(payload.environment_id)
        rocket = await self._load_rocket(payload.rocket_id)
        flight_model = payload.flight.assemble(
            environment=environment,
            rocket=rocket,
        )
        flight_model.set_id(flight_id)
        await self.put_flight_by_id(flight_id, flight_model)
        return

    @controller_exception_handler
    async def update_environment_by_flight_id(
        self, flight_id: str, *, environment: EnvironmentModel
    ) -> None:
        """
        Update a models.Flight.environment in the database.

        Args:
            flight_id: str
            environment: models.Environment

        Returns:
            None

        Raises:
            HTTP 404 Not Found: If the flight is not found in the database.
        """
        flight = await self.get_flight_by_id(flight_id)
        flight.environment = environment
        await self.update_flight_by_id(flight_id, flight)
        return

    @controller_exception_handler
    async def update_rocket_by_flight_id(
        self, flight_id: str, *, rocket: RocketModel
    ) -> None:
        """
        Update a models.Flight.rocket in the database.

        Args:
            flight_id: str
            rocket: models.Rocket

        Returns:
            None

        Raises:
            HTTP 404 Not Found: If the flight is not found in the database.
        """
        flight = await self.get_flight_by_id(flight_id)
        flight.rocket = rocket
        await self.update_flight_by_id(flight_id, flight)
        return

    @controller_exception_handler
    async def get_rocketpy_flight_binary(
        self,
        flight_id: str,
    ) -> bytes:
        """
        Get rocketpy.flight as dill binary.

        Args:
            flight_id: str

        Returns:
            bytes

        Raises:
            HTTP 404 Not Found: If the flight is not found in the database.
        """
        flight = await self.get_flight_by_id(flight_id)
        flight_service = FlightService.from_flight_model(flight.flight)
        return flight_service.get_flight_binary()

    @controller_exception_handler
    async def get_flight_simulation(
        self,
        flight_id: str,
    ) -> FlightSimulation:
        """
        Simulate a rocket flight.

        Args:
            flight_id: str

        Returns:
            Flight simulation view.

        Raises:
            HTTP 404 Not Found: If the flight does not exist in the database.
        """
        flight = await self.get_flight_by_id(flight_id)
        flight_service = FlightService.from_flight_model(flight.flight)
        return flight_service.get_flight_simulation()
