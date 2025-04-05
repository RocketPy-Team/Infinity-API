from src.controllers.interface import (
    ControllerBase,
    controller_exception_handler,
)
from src.views.flight import FlightSimulation
from src.models.flight import FlightModel
from src.models.environment import EnvironmentModel
from src.models.rocket import RocketModel
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
