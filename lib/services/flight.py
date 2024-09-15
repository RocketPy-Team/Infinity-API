from typing import Self

import dill

from rocketpy.simulation.flight import Flight as RocketPyFlight
from rocketpy.utilities import get_instance_attributes

from lib.models.flight import Flight
from lib.services.environment import EnvironmentService
from lib.services.rocket import RocketService
from lib.views.flight import FlightSummary


class FlightService:
    _flight: RocketPyFlight

    def __init__(self, flight: RocketPyFlight = None):
        self._flight = flight

    @classmethod
    def from_flight_model(cls, flight: Flight) -> Self:
        """
        Get the rocketpy flight object.

        Returns:
            FlightService containing the rocketpy flight object.
        """
        rocketpy_env = EnvironmentService.from_env_model(
            flight.environment
        ).environment
        rocketpy_rocket = RocketService.from_rocket_model(flight.rocket).rocket
        rocketpy_flight = RocketPyFlight(
            rocket=rocketpy_rocket,
            inclination=flight.inclination,
            heading=flight.heading,
            environment=rocketpy_env,
            rail_length=flight.rail_length,
            #   initial_solution=flight.initial_solution,
            terminate_on_apogee=flight.terminate_on_apogee,
            max_time=flight.max_time,
            max_time_step=flight.max_time_step,
            min_time_step=flight.min_time_step,
            rtol=flight.rtol,
            atol=flight.atol,
            time_overshoot=flight.time_overshoot,
            verbose=flight.verbose,
            equations_of_motion=flight.equations_of_motion.value.lower(),
        )
        return cls(flight=rocketpy_flight)

    @property
    def flight(self) -> RocketPyFlight:
        return self._flight

    @flight.setter
    def flight(self, flight: RocketPyFlight):
        self._flight = flight

    def get_flight_summary(self) -> FlightSummary:
        """
        Get the summary of the flight.

        Returns:
            FlightSummary
        """
        attributes = get_instance_attributes(self.flight)
        flight_summary = FlightSummary(**attributes)
        return flight_summary

    def get_flight_binary(self) -> bytes:
        """
        Get the binary representation of the flight.

        Returns:
            bytes
        """
        return dill.dumps(self.flight)
