from typing import Dict, Any, Union
from fastapi import Response, status

import rocketpy.Flight
import jsonpickle

from lib.models.rocket import Rocket
from lib.models.flight import Flight
from lib.models.environment import Env
from lib.views.flight import FlightSummary, SurfaceWindConditions, OutOfRailConditions, BurnoutConditions, ApogeeConditions, MaximumValues, InitialConditions, NumericalIntegrationSettings, ImpactConditions, EventsRegistered, LaunchRailConditions, FlightData, FlightCreated, FlightUpdated, FlightDeleted, FlightPickle
from lib.repositories.flight import FlightRepository
from lib.controllers.environment import EnvController
from lib.controllers.rocket import RocketController


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
                environment=rocketpy_env,
                rail_length=flight.rail_length,
        )
        self.rocketpy_flight = rocketpy_flight
        self.flight = flight

    def create_flight(self) -> "Dict[str, str]":
        """
        Create a flight in the database.

        Returns:
            Dict[str, str]: Flight id.
        """
        flight = FlightRepository(flight=self.flight)
        successfully_created_flight = flight.create_flight()
        if successfully_created_flight:
            return FlightCreated(flight_id=str(flight.flight_id))
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
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
        successfully_read_flight = \
            FlightRepository(flight_id=flight_id).get_flight()
        if not successfully_read_flight:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
        return successfully_read_flight

    @staticmethod
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
        successfully_read_flight = \
            FlightRepository(flight_id=flight_id).get_flight()
        if not successfully_read_flight:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        successfully_read_rocketpy_flight = \
            FlightController(successfully_read_flight).rocketpy_flight

        return FlightPickle(jsonpickle_rocketpy_flight=jsonpickle.encode(successfully_read_rocketpy_flight))

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
        successfully_read_flight = \
            FlightRepository(flight_id=flight_id).get_flight()
        if not successfully_read_flight:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        successfully_updated_flight = \
            FlightRepository(flight=self.flight, flight_id=flight_id).update_flight()

        if successfully_updated_flight:
            return FlightUpdated(new_flight_id=str(successfully_updated_flight))
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
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
        successfully_read_flight = \
            FlightRepository(flight_id=flight_id).get_flight()
        if not successfully_read_flight:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
        flight = successfully_read_flight

        flight.env = env
        successfully_updated_flight = \
            FlightRepository(flight=flight).update_flight(flight_id)
        if successfully_updated_flight:
            return {
                    "message": "Flight updated successfully",
                    "new_flight_id": str(successfully_updated_flight)
            }
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
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
        successfully_read_flight = \
            FlightRepository(flight_id=flight_id).get_flight()
        if not successfully_read_flight:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
        flight = successfully_read_flight

        flight.rocket = rocket
        successfully_updated_flight = \
            FlightRepository(flight=flight).update_flight(flight_id)
        if successfully_updated_flight:
            return {
                    "message": "Flight updated successfully",
                    "new_flight_id": str(successfully_updated_flight)
            }
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
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
        successfully_read_flight = \
            FlightRepository(flight_id=flight_id).get_flight()
        if not successfully_read_flight:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        successfully_deleted_flight = \
            FlightRepository(flight_id=flight_id).delete_flight()
        if successfully_deleted_flight:
            return FlightDeleted(deleted_flight_id=str(flight_id))
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def simulate(flight_id: int) -> "Union[FlightSummary, Response]":
        """
        Simulate a rocket flight.

        Args:
            flight_id (int): Flight id.

        Returns:
            Flight summary view.

        Raises:
            HTTP 404 Not Found: If the flight does not exist in the database.
        """
        successfully_read_flight = \
            FlightRepository(flight_id=flight_id).get_flight()
        if not successfully_read_flight:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        flight = FlightController(successfully_read_flight).rocketpy_flight

        _initial_conditions = InitialConditions(
            initial_altitude = "Attitude - e0: {:.3f} | e1: {:.3f} | e2: {:.3f} | e3: {:.3f}".format(flight.e0(0), flight.e1(0), flight.e2(0), flight.e3(0)),
            initial_velocity = "Velocity - Vx: {:.2f} m/s | Vy: {:.2f} m/s | Vz: {:.2f} m/s".format(flight.vx(0), flight.vy(0), flight.vz(0)),
            initial_position = "Position - x: {:.2f} m | y: {:.2f} m | z: {:.2f} m".format(flight.x(0), flight.y(0), flight.z(0)),
            initial_angular_position = "Euler Angles - Spin φ : {:.2f}° | Nutation θ: {:.2f}° | Precession ψ: {:.2f}°".format(flight.phi(0), flight.theta(0), flight.psi(0)),
            initial_angular_velocity = "Angular Velocity - ω1: {:.2f} rad/s | ω2: {:.2f} rad/s| ω3: {:.2f} rad/s".format(flight.w1(0), flight.w2(0), flight.w3(0))
        )

        _numerical_integration_settings = NumericalIntegrationSettings(
            max_time = "Maximum Allowed Flight Time: {:f} s".format(flight.max_time),
            max_time_step = "Maximum Allowed Time Step: {:f} s".format(flight.max_time_step),
            min_time_step = "Minimum Allowed Time Step: {:e} s".format(flight.min_time_step),
            relative_error_tolerance = f"Relative Error Tolerance: {flight.rtol}",
            absolute_error_tolerance = f"Absolute Error Tolerance: {flight.atol}",
            time_overshoot = f"Allow Event Overshoot: {flight.time_overshoot}",
            terminate_on_apogee = f"Terminate Simulation on Apogee: {flight.terminate_on_apogee}",
            number_of_time_steps = f"Number of Time Steps Used: {len(flight.time_steps)}",
            function_evaluations_per_time_step = f"Number of Derivative Functions Evaluation: {sum(flight.function_evaluations_per_time_step)}",
            avg_function_evaluations_per_time_step = "Average Function Evaluations per Time Step: {:3f}".format(sum(flight.function_evaluations_per_time_step) / len(flight.time_steps))
        )

        _launch_rail_conditions = LaunchRailConditions(
            rail_length = "Launch Rail Length: {:.2f} m".format(flight.rail_length),
            flight_inclination = "Launch Rail Inclination: {:.2f}°".format(flight.inclination),
            flight_heading = "Launch Rail Heading: {:.2f}°".format(flight.heading)
        )

        _surface_wind_conditions = SurfaceWindConditions(
            frontal_surface_wind_speed = "Frontal Surface Wind Speed: {:.2f} m/s".format(flight.frontal_surface_wind),
            lateral_surface_wind_speed = "Lateral Surface Wind Speed: {:.2f} m/s".format(flight.lateral_surface_wind)
        )

        _out_of_rail_conditions = OutOfRailConditions(
            out_of_rail_time = "Rail Departure Time: {:.3f} s".format(flight.out_of_rail_time),
            out_of_rail_velocity =  "Rail Departure Velocity: {:.3f} m/s".format(flight.out_of_rail_velocity),
            out_of_rail_static_margin = "Rail Departure Static Margin: {:.3f} c".format(flight.rocket.static_margin(flight.out_of_rail_time)),
            out_of_rail_angle_of_attack = "Rail Departure Angle of Attack: {:.3f}°".format(flight.angle_of_attack(flight.out_of_rail_time)),
            out_of_rail_thrust_weight_ratio = "Rail Departure Thrust-Weight Ratio: {:.3f}".format(flight.rocket.thrust_to_weight(flight.out_of_rail_time)),
            out_of_rail_reynolds_number = "Rail Departure Reynolds Number: {:.3e}".format(flight.reynolds_number(flight.out_of_rail_time))
        )

        _burnout_conditions = BurnoutConditions(
            burnout_time = "Burn out time: {:.3f} s".format(flight.rocket.motor.burn_out_time),
            burnout_altitude = "Altitude at burn out: {:.3f} m (AGL)".format(
                flight.z(flight.rocket.motor.burn_out_time)
                - flight.env.elevation
            ),
            burnout_rocket_velocity = "Rocket velocity at burn out: {:.3f} m/s".format(
                flight.speed(flight.rocket.motor.burn_out_time)
            ),
            burnout_freestream_velocity = "Freestream velocity at burn out: {:.3f} m/s".format((
                flight.stream_velocity_x(flight.rocket.motor.burn_out_time) ** 2
                + flight.stream_velocity_y(flight.rocket.motor.burn_out_time) ** 2
                + flight.stream_velocity_z(flight.rocket.motor.burn_out_time) ** 2
            )
            ** 0.5),
            burnout_mach_number = "Mach Number at burn out: {:.3f}".format(flight.mach_number(flight.rocket.motor.burn_out_time)),
            burnout_kinetic_energy = "Kinetic energy at burn out: {:.3e}".format(flight.kinetic_energy(flight.rocket.motor.burn_out_time))
        )

        _apogee_conditions = ApogeeConditions(
            apogee_altitude = "Apogee Altitude: {:.3f} m (ASL) | {:.3f} m (AGL)".format(flight.apogee, flight.apogee - flight.env.elevation),
            apogee_time = "Apogee Time: {:.3f} s".format(flight.apogee_time),
            apogee_freestream_speed = "Apogee Freestream Speed: {:.3f} m/s".format(flight.apogee_freestream_speed)
        )

        _maximum_values = MaximumValues(
            maximum_speed = "Maximum Speed: {:.3f} m/s at {:.2f} s".format(flight.max_speed, flight.max_speed_time),
            maximum_mach_number  = "Maximum Mach Number: {:.3f} Mach at {:.2f} s".format(flight.max_mach_number, flight.max_mach_number_time),
            maximum_reynolds_number = "Maximum Reynolds Number: {:.3e} at {:.2f} s".format(flight.max_reynolds_number, flight.max_reynolds_number_time),
            maximum_dynamic_pressure = "Maximum Dynamic Pressure: {:.3e} Pa at {:.2f} s".format(flight.max_dynamic_pressure, flight.max_dynamic_pressure_time),
            maximum_acceleration_during_motor_burn  = "Maximum Acceleration During Motor Burn: {:.3f} m/s² at {:.2f} s".format(flight.max_acceleration, flight.max_acceleration_time),
            maximum_gs_during_motor_burn = "Maximum Gs During Motor Burn: {:.3f} g at {:.2f} s".format(flight.max_acceleration / flight.env.gravity(flight.z(flight.max_acceleration_time)), flight.max_acceleration_time),
            maximum_acceleration_after_motor_burn = "Maximum Acceleration After Motor Burn: {:.3f} m/s² at {:.2f} s".format(
                flight.max_acceleration_power_off,
                flight.max_acceleration_power_off_time,
            ),
            maximum_gs_after_motor_burn = "Maximum Gs After Motor Burn: {:.3f} g at {:.2f} s".format(
                flight.max_acceleration_power_off / flight.env.standard_g,
                flight.max_acceleration_power_off_time,
            ),
            maximum_upper_rail_button_normal_force = "Maximum Upper Rail Button Normal Force: {:.3f} N".format(flight.max_rail_button1_normal_force),
            maximum_upper_rail_button_shear_force = "Maximum Upper Rail Button Shear Force: {:.3f} N".format(flight.max_rail_button1_shear_force),
            maximum_lower_rail_button_normal_force = "Maximum Lower Rail Button Normal Force: {:.3f} N".format(flight.max_rail_button2_normal_force),
            maximum_lower_rail_button_shear_force = "Maximum Lower Rail Button Shear Force: {:.3f} N".format(flight.max_rail_button2_shear_force)
        )

        if len(flight.impact_state) != 0:
            _impact_conditions = ImpactConditions(
                x_impact_position = "X Impact: {:.3f} m".format(flight.x_impact),
                y_impact_position = "Y Impact: {:.3f} m".format(flight.y_impact),
                time_of_impact = "Time of Impact: {:.3f} s".format(flight.t_final),
                impact_velocity = "Velocity at Impact: {:.3f} m/s".format(flight.impact_velocity)
            )
        elif flight.terminate_on_apogee is False:
            _impact_conditions = ImpactConditions(
                time = "Time: {:.3f} s".format(flight.solution[-1][0]),
                altitude = "Altitude: {:.3f} m".format(flight.solution[-1][3])
            )

        if len(flight.parachute_events) == 0:
            _events_registered = EventsRegistered(
                events_trace = "No parachute event registered"
            )
        else:
            events = { }
            for event in flight.parachute_events:
                trigger_time = event[0]
                parachute = event[1]
                open_time = trigger_time + parachute.lag
                velocity = flight.free_stream_speed(open_time)
                altitude = flight.z(open_time)
                name = parachute.name.title()
                events[name] = []
                events[name].append(name + " Ejection Triggered at: {:.3f} s".format(trigger_time))
                events[name].append(name + " Parachute Inflated at: {:.3f} s".format(open_time))
                events[name].append(
                    name
                    + " Parachute Inflated with Freestream Speed of: {:.3f} m/s".format(
                        velocity
                    )
                )
                events[name].append(
                    name
                    + " Parachute Inflated at Height of: {:.3f} m (AGL)".format(
                        altitude - flight.env.elevation
                    )
                )
            _events_registered = EventsRegistered(
                events_trace = events
            )

        _flight_data = FlightData(
            initial_conditions = _initial_conditions,
            numerical_integration_settings = _numerical_integration_settings,
            surface_wind_conditions = _surface_wind_conditions,
            launch_rail_conditions = _launch_rail_conditions,
            out_of_rail_conditions= _out_of_rail_conditions,
            burnout_conditions = _burnout_conditions,
            apogee_conditions = _apogee_conditions,
            maximum_values = _maximum_values,
            impact_conditions = _impact_conditions,
            events_registered = _events_registered
        )

        flight_summary = FlightSummary( flight_data = _flight_data )

        return flight_summary
