from lib.models.rocket import Rocket
from lib.models.flight import Flight
from lib.models.environment import Env
from lib.views import FlightSummary, SurfaceWindConditions, RailDepartureState, BurnoutState, Apogee, MaximumValues
from lib.repositories.flight import FlightRepository 
from lib.controllers.environment import EnvController
from lib.controllers.rocket import RocketController

from typing import Dict, Any, Union
from fastapi import Response, status

import rocketpy.Flight
import jsonpickle

class FlightController():
    """
    Controller for the Flight model.

    Init Attributes:
        flight (models.Flight): Flight model object.

    Enables:
        - Create a rocketpy.Flight object from a Flight model object.
        - Generate trajectory simulation from a rocketpy.Flight object.
        - Create both Flight model and rocketpy.Flight objects in the database.
        - Update both Flight model and rocketpy.Flight objects in the database.
        - Delete both Flight model and rocketpy.Flight objects from the database.
        - Read a Flight model from the database.
        - Read a rocketpy.Flight object from the database.

    """
    def __init__(self, flight: Flight):
        rocketpy_rocket = RocketController(flight.rocket).rocketpy_rocket
        rocketpy_env = EnvController(flight.environment).rocketpy_env

        rocketpy_flight=rocketpy.Flight(
                rocket=rocketpy_rocket,
                inclination=flight.inclination, 
                heading=flight.heading,
                environment=rocketpy_env
        )
        self.rocketpy_flight = rocketpy_flight 
        self.flight = flight

    def simulate(flight_id: int) -> "FlightSummary":
        """
        Simulate a rocket flight.

        Args:
            flight_id (int): Flight id.

        Returns:
            Flight summary view.

        Raises:
            HTTP 404 Not Found: If the flight does not exist in the database.
        """
        successfully_read_flight = FlightRepository(flight_id=flight_id).get_flight()
        if not successfully_read_flight:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        flight = FlightController(successfully_read_flight).rocketpy_flight

        _surface_wind_conditions = SurfaceWindConditions(
            frontal_surface_wind_speed = "{:.2f} m/s".format(flight.frontalSurfaceWind),
            lateral_surface_wind_speed = "{:.2f} m/s".format(flight.lateralSurfaceWind)
        )

        _rail_departure_state = RailDepartureState(
            rail_departure_time = "{:.3f} s".format(flight.outOfRailTime),
            rail_departure_velocity =  "{:.3f} m/s".format(flight.outOfRailVelocity),
            rail_departure_static_margin = "{:.3f} c".format(flight.rocket.staticMargin(flight.outOfRailTime)),
            rail_departure_angle_of_attack = "{:.3f}°".format(flight.angleOfAttack(flight.outOfRailTime)),
            rail_departure_thrust_weight_ratio = "{:.3f}".format(flight.rocket.thrustToWeight(flight.outOfRailTime)),
            rail_departure_reynolds_number = "{:.3e}".format(flight.ReynoldsNumber(flight.outOfRailTime))
        )

        _burnout_state = BurnoutState(
            burnout_time = "{:.3f} s".format(flight.rocket.motor.burnOutTime),
            altitude_at_burnout = "{:.3f} m/s".format(flight.speed(flight.rocket.motor.burnOutTime)),
            rocket_velocity_at_burnout = "{:.3f} m/s".format(flight.speed(flight.rocket.motor.burnOutTime)),
            freestream_velocity_at_burnout = "{:.3f} m/s".format((
                flight.streamVelocityX(flight.rocket.motor.burnOutTime) ** 2
                + flight.streamVelocityY(flight.rocket.motor.burnOutTime) ** 2
                + flight.streamVelocityZ(flight.rocket.motor.burnOutTime) ** 2
            )
            ** 0.5),
            mach_number_at_burnout = "{:.3f}".format(flight.MachNumber(flight.rocket.motor.burnOutTime)),
            kinetic_energy_at_burnout = "{:.3e}".format(flight.kineticEnergy(flight.rocket.motor.burnOutTime))
        )

        _apogee = Apogee(
            apogee_altitude = "{:.3f} m (ASL) | {:.3f} m (AGL)".format(flight.apogee, flight.apogee - flight.env.elevation),
            apogee_time = "{:.3f} s".format(flight.apogeeTime),
            apogee_freestream_speed = "{:.3f} m/s".format(flight.apogeeFreestreamSpeed)
        )

        _maximum_values = MaximumValues(
            maximum_speed = "{:.3f} m/s at {:.2f} s".format(flight.maxSpeed, flight.maxSpeedTime),
            maximum_mach_number  = "{:.3f} Mach at {:.2f} s".format(flight.maxMachNumber, flight.maxMachNumberTime),
            maximum_reynolds_number = "{:.3e} at {:.2f} s".format(flight.maxReynoldsNumber, flight.maxReynoldsNumberTime),
            maximum_dynamic_pressure = "{:.3e} Pa at {:.2f} s".format(flight.maxDynamicPressure, flight.maxDynamicPressureTime),
            maximum_acceleration  = "{:.3f} m/s² at {:.2f} s".format(flight.maxAcceleration, flight.maxAccelerationTime),
            maximum_gs = "{:.3f} g at {:.2f} s".format(flight.maxAcceleration / flight.env.gravity(flight.z(flight.maxAccelerationTime)), flight.maxAccelerationTime),
            maximum_upper_rail_button_normal_force = "{:.3f} N".format(flight.maxRailButton1NormalForce),
            maximum_upper_rail_button_shear_force = "{:.3f} N".format(flight.maxRailButton1ShearForce),
            maximum_lower_rail_button_normal_force = "{:.3f} N".format(flight.maxRailButton2NormalForce),
            maximum_lower_rail_button_shear_force = "{:.3f} N".format(flight.maxRailButton2ShearForce)
        )

        flight_summary = FlightSummary(
            surface_wind_conditions = _surface_wind_conditions, 
            rail_departure_state = _rail_departure_state,
            burnout_state = _burnout_state,
            apogee = _apogee,
            maximum_values = _maximum_values, 
        )

        return flight_summary

    def create_flight(self) -> "Dict[str, str]":
        """
        Create a flight in the database.

        Returns:
            Dict[str, str]: Flight id.
        """
        flight = FlightRepository(flight=self.flight)
        successfully_created_flight = flight.create_flight()
        if successfully_created_flight: 
            return { "message": "Flight created", "flight_id": flight.flight_id }
        else:
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_flight(flight_id: int) -> "Union[Flight, Response]":
        """
        Get a flight from the database.

        Args:
            flight_id (int): Flight id.

        Returns:
            Flight model object

        Raises:
            HTTP 404 Not Found: If the flight is not found in the database. 
        """
        successfully_read_flight = FlightRepository(flight_id=flight_id).get_flight()
        if not successfully_read_flight:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
        return successfully_read_flight

    def get_rocketpy_flight(flight_id: int) -> "Union[Dict[str, Any], Response]":
        """
        Get a rocketpy flight object encoded as jsonpickle string from the database.

        Args:
            flight_id (int): Flight id.

        Returns:
            str: jsonpickle string of the rocketpy flight.

        Raises:
            HTTP 404 Not Found: If the flight is not found in the database.
        """
        successfully_read_flight = FlightRepository(flight_id=flight_id).get_flight()
        if not successfully_read_flight:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        successfully_read_rocketpy_flight = FlightController(successfully_read_flight).rocketpy_flight

        return { "jsonpickle_rocketpy_flight": jsonpickle.encode(successfully_read_rocketpy_flight) }
           
    def update_flight(self, flight_id: int) -> "Union[Dict[str, Any], Response]":
        """
        Update a flight in the database.

        Args:
            flight_id (int): Flight id.

        Returns:
            Dict[str, Any]: Flight id and message.

        Raises:
            HTTP 404 Not Found: If the flight is not found in the database.
        """
        successfully_read_flight = FlightRepository(flight_id=flight_id).get_flight()
        if not successfully_read_flight:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        successfully_updated_flight = \
                FlightRepository(flight=self.flight, flight_id=flight_id).update_flight()

        if successfully_updated_flight:
            return { 
                    "message": "Flight updated successfully", 
                    "new_flight_id": successfully_updated_flight
            }
        else:
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update_env(flight_id: int, env: Env) -> "Union[Dict[str, Any], Response]":
        """
        Update the environment of a flight in the database.

        Args:
            flight_id (int): Flight id.
            env (models.Env): Environment model object.

        Returns:
            Dict[str, Any]: Flight id and message.

        Raises:
            HTTP 404 Not Found: If the flight is not found in the database.
        """
        successfully_read_flight = FlightRepository(flight_id=flight_id).get_flight()
        if not successfully_read_flight:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        flight.env = env
        successfully_updated_flight = FlightRepository(flight=flight).update_flight(flight_id)
        if successfully_updated_flight:
            return { 
                    "message": "Flight updated successfully", 
                    "new_flight_id": successfully_updated_flight
            }
        else:
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update_rocket(flight_id: int, rocket: Rocket) -> "Union[Dict[str, Any], Response]":
        """
        Update the rocket of a flight in the database.

        Args:
            flight_id (int): Flight id.
            rocket (models.Rocket): Rocket model object.

        Returns:
            Dict[str, Any]: Flight id and message.

        Raises:
            HTTP 404 Not Found: If the flight is not found in the database.
        """
        successfully_read_flight = FlightRepository(flight_id=flight_id).get_flight()
        if not successfully_read_flight:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        flight.rocket = rocket 
        successfully_updated_flight = FlightRepository(flight=flight).update_flight(flight_id) 
        if successfully_updated_flight:
            return { 
                    "message": "Flight updated successfully", 
                    "new_flight_id": successfully_updated_flight
            }
        else:
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete_flight(flight_id: int) -> "Union[Dict[str, str], Response]":
        """
        Delete a flight from the database.

        Args:
            flight_id (int): Flight id.

        Returns:
            Dict[str, str]: Flight id and message.

        Raises:
            HTTP 404 Not Found: If the flight is not found in the database.
        """
        successfully_read_flight = FlightRepository(flight_id=flight_id).get_flight()
        if not successfully_read_flight:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        successfully_deleted_flight = FlightRepository(flight_id=flight_id).delete_flight()
        if successfully_deleted_flight: 
            return {"flight_id": flight_id, "message": "Flight deleted successfully"}
        else:
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
