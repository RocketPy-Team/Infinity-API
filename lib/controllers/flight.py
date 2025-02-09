from lib.controllers.interface import (
    ControllerInterface,
    controller_exception_handler,
)
from lib.views.flight import FlightSummary, FlightUpdated
from lib.models.flight import FlightModel
from lib.models.environment import EnvironmentModel
from lib.models.rocket import RocketModel
from lib.services.flight import FlightService


class FlightController(ControllerInterface):
    """
    Controller for the Flight model.

    Enables:
        - Simulation of a RocketPy Flight.
        - CRUD for Flight BaseApiModel.
    """

    def __init__(self):
        super().__init__(models=[FlightModel])

    @controller_exception_handler
    async def update_env_by_flight_id(
        self, flight_id: str, *, env: EnvironmentModel
    ) -> FlightUpdated:
        """
        Update a models.Flight.env in the database.

        Args:
            flight_id: str
            env: models.Env

        Returns:
            views.FlightUpdated

        Raises:
            HTTP 404 Not Found: If the flight is not found in the database.
        """
        flight = await self.get_flight_by_id(flight_id)
        flight.environment = env
        self.update_flight_by_id(flight_id, flight)
        return FlightUpdated(flight_id=flight_id)

    @controller_exception_handler
    async def update_rocket_by_flight_id(
        self, flight_id: str, *, rocket: RocketModel
    ) -> FlightUpdated:
        """
        Update a models.Flight.rocket in the database.

        Args:
            flight_id: str
            rocket: models.Rocket

        Returns:
            views.FlightUpdated

        Raises:
            HTTP 404 Not Found: If the flight is not found in the database.
        """
        flight = await self.get_flight_by_id(flight_id)
        flight.rocket = rocket
        self.update_flight_by_id(flight_id, flight)
        return FlightUpdated(flight_id=flight_id)

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
        flight_service = FlightService.from_flight_model(flight)
        return flight_service.get_flight_binary()

    @controller_exception_handler
    async def simulate_flight(
        self,
        flight_id: str,
    ) -> FlightSummary:
        """
        Simulate a rocket flight.

        Args:
            flight_id: str

        Returns:
            Flight summary view.

        Raises:
            HTTP 404 Not Found: If the flight does not exist in the database.
        """
        flight = await self.get_flight_by_id(flight_id=flight_id)
        flight_service = FlightService.from_flight_model(flight)
        return flight_service.get_flight_summary()
