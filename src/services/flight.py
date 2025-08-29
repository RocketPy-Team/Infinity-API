from typing import Self

import dill

from rocketpy.simulation.flight import Flight as RocketPyFlight

from src.services.environment import EnvironmentService
from src.services.rocket import RocketService
from src.models.flight import FlightModel
from src.views.flight import FlightSimulation
from src.views.rocket import RocketSimulation
from src.views.motor import MotorSimulation
from src.views.environment import EnvironmentSimulation
from src.utils import collect_attributes


class FlightService:
    _flight: RocketPyFlight

    def __init__(self, flight: RocketPyFlight = None):
        self._flight = flight

    @classmethod
    def from_flight_model(cls, flight: FlightModel) -> Self:
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
            environment=rocketpy_env,
            rail_length=flight.rail_length,
            terminate_on_apogee=flight.terminate_on_apogee,
            time_overshoot=flight.time_overshoot,
            equations_of_motion=flight.equations_of_motion,
            **flight.get_additional_parameters(),
        )
        return cls(flight=rocketpy_flight)

    @property
    def flight(self) -> RocketPyFlight:
        return self._flight

    @flight.setter
    def flight(self, flight: RocketPyFlight):
        self._flight = flight

    def get_flight_simulation(self) -> FlightSimulation:
        """
        Get the simulation of the flight.

        Returns:
            FlightSimulation
        """
        encoded_attributes = collect_attributes(
            self.flight,
            [
                FlightSimulation,
                RocketSimulation,
                MotorSimulation,
                EnvironmentSimulation,
            ],
        )
        flight_simulation = FlightSimulation(**encoded_attributes)
        return flight_simulation

    def get_flight_binary(self) -> bytes:
        """
        Get the binary representation of the flight.

        Returns:
            bytes
        """
        return dill.dumps(self.flight)
