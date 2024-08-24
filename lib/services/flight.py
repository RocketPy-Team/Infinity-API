from typing import Self

from rocketpy.simulation.flight import Flight as RocketPyFlight
from rocketpy.utilities import get_instance_attributes

from lib.models.flight import Flight
from lib.services.environment import EnvironmentService
from lib.services.rocket import RocketService
from lib.views.flight import FlightSummary


class FlightService(RocketPyFlight):

    @classmethod
    def from_flight_model(cls, flight: Flight) -> Self:
        """
        Get the rocketpy flight object.

        Returns:
            RocketPyFlight
        """
        rocketpy_rocket = RocketService.from_rocket_model(flight.rocket)
        rocketpy_env = EnvironmentService.from_env_model(flight.environment)
        rocketpy_flight = RocketPyFlight(
            rocket=rocketpy_rocket,
            inclination=flight.inclination,
            heading=flight.heading,
            environment=rocketpy_env,
            rail_length=flight.rail_length,
        )
        return rocketpy_flight

    def get_flight_summary(self) -> FlightSummary:
        """
        Get the summary of the flight.

        Returns:
            FlightSummary
        """
        attributes = get_instance_attributes(self)
        flight_summary = FlightSummary(**attributes)
        return flight_summary
