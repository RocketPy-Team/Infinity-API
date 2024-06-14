from typing import Union
from fastapi import HTTPException, status
from pymongo.errors import PyMongoError

from rocketpy.simulation.flight import Flight as RocketPyFlight

import jsonpickle

from lib import logger, parse_error
from lib.models.rocket import Rocket, RocketOptions
from lib.models.motor import MotorKinds
from lib.models.flight import Flight
from lib.models.environment import Env
from lib.views.flight import (
    FlightSummary,
    SurfaceWindConditions,
    OutOfRailConditions,
    BurnoutConditions,
    ApogeeConditions,
    MaximumValues,
    InitialConditions,
    NumericalIntegrationSettings,
    ImpactConditions,
    EventsRegistered,
    LaunchRailConditions,
    FlightData,
    FlightCreated,
    FlightUpdated,
    FlightDeleted,
    FlightPickle,
)
from lib.repositories.flight import FlightRepository
from lib.controllers.environment import EnvController
from lib.controllers.rocket import RocketController
from lib.services.environment import EnvironmentService


class FlightController:
    """
    Controller for the Flight model.

    Init Attributes:
        flight (models.Flight): Flight model object.

    Enables:
        - Create a RocketPyFlight object from a Flight model object.
        - Generate trajectory simulation from a RocketPyFlight object.
        - Create both Flight model and RocketPyFlight objects in the database.
        - Update both Flight model and RocketPyFlight objects in the database.
        - Delete both Flight model and RocketPyFlight objects from the database.
        - Read a Flight model from the database.
        - Read a RocketPyFlight object from the database.

    """

    def __init__(
        self,
        flight: Flight,
        *,
        rocket_option: RocketOptions,
        motor_kind: MotorKinds,
    ):
        self._flight = flight
        self._rocket_option = rocket_option
        self._motor_kind = motor_kind

    @property
    def flight(self) -> Flight:
        return self._flight

    @property
    def rocket_option(self) -> RocketOptions:
        return self._rocket_option

    @property
    def motor_kind(self) -> MotorKinds:
        return self._motor_kind

    @flight.setter
    def flight(self, flight: Flight):
        self._flight = flight

    @staticmethod
    def get_rocketpy_flight(flight: Flight) -> RocketPyFlight:
        """
        Get the rocketpy flight object.

        Returns:
            RocketPyFlight
        """
        rocketpy_rocket = RocketController.get_rocketpy_rocket(flight.rocket)
        rocketpy_env = EnvironmentService.from_env_model(flight.environment)
        rocketpy_flight = RocketPyFlight(
            rocket=rocketpy_rocket,
            inclination=flight.inclination,
            heading=flight.heading,
            environment=rocketpy_env,
            rail_length=flight.rail_length,
        )
        return rocketpy_flight

    async def create_flight(self) -> Union[FlightCreated, HTTPException]:
        """
        Create a flight in the database.

        Returns:
            views.FlightCreated
        """
        try:
            async with FlightRepository() as flight_repo:
                flight_repo.fetch_flight(self.flight)
                await flight_repo.create_flight(
                    motor_kind=self.motor_kind,
                    rocket_option=self.rocket_option,
                )
        except PyMongoError as e:
            logger.error(f"controllers.flight.create_flight: PyMongoError {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to create flight in db",
            ) from e
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.flight.create_flight: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create flight: {exc_str}",
            ) from e
        else:
            return FlightCreated(flight_id=self.flight.flight_id)
        finally:
            logger.info(
                f"Call to controllers.flight.create_flight completed for Flight {hash(self.flight)}"
            )

    @staticmethod
    async def get_flight_by_id(flight_id: str) -> Union[Flight, HTTPException]:
        """
        Get a flight from the database.

        Args:
            flight_id: str

        Returns:
            models.Flight

        Raises:
            HTTP 404 Not Found: If the flight is not found in the database.
        """
        try:
            async with FlightRepository() as flight_repo:
                await flight_repo.get_flight_by_id(flight_id)
                read_flight = flight_repo.flight
        except PyMongoError as e:
            logger.error(
                f"controllers.flight.get_flight_by_id: PyMongoError {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to read flight from db",
            ) from e
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.flight.get_flight_by_id: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read flight: {exc_str}",
            ) from e
        else:
            if read_flight:
                return read_flight
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Flight not found.",
            )
        finally:
            logger.info(
                f"Call to controllers.flight.get_flight_by_id completed for Flight {flight_id}"
            )

    @classmethod
    async def get_rocketpy_flight_as_jsonpickle(
        cls,
        flight_id: str,
    ) -> Union[FlightPickle, HTTPException]:
        """
        Get rocketpy.flight as jsonpickle string.

        Args:
            flight_id: str

        Returns:
            views.FlightPickle

        Raises:
            HTTP 404 Not Found: If the flight is not found in the database.
        """
        try:
            read_flight = await cls.get_flight_by_id(flight_id)
            rocketpy_flight = cls.get_rocketpy_flight(read_flight)
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(
                f"controllers.flight.get_rocketpy_flight_as_jsonpickle: {exc_str}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read flight: {exc_str}",
            ) from e
        else:
            return FlightPickle(
                jsonpickle_rocketpy_flight=jsonpickle.encode(rocketpy_flight)
            )
        finally:
            logger.info(
                f"Call to controllers.flight.get_rocketpy_flight_as_jsonpickle completed for Flight {flight_id}"
            )

    async def update_flight_by_id(
        self, flight_id: str
    ) -> Union[FlightUpdated, HTTPException]:
        """
        Update a models.Flight in the database.

        Args:
            flight_id: str

        Returns:
            views.FlightUpdated

        Raises:
            HTTP 404 Not Found: If the flight is not found in the database.
        """
        try:
            async with FlightRepository() as flight_repo:
                flight_repo.fetch_flight(self.flight)
                await flight_repo.create_flight(
                    motor_kind=self.motor_kind,
                    rocket_option=self.rocket_option,
                )
                await flight_repo.delete_flight_by_id(flight_id)
        except PyMongoError as e:
            logger.error(f"controllers.flight.update_flight: PyMongoError {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to update flight in db",
            ) from e
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.flight.update_flight: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update flight: {exc_str}",
            ) from e
        else:
            return FlightUpdated(new_flight_id=self.flight.flight_id)
        finally:
            logger.info(
                f"Call to controllers.flight.update_flight completed for Flight {flight_id}"
            )

    @classmethod
    async def update_env_by_flight_id(
        cls, flight_id: str, *, env: Env
    ) -> Union[FlightUpdated, HTTPException]:
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
        try:
            read_flight = await cls.get_flight_by_id(flight_id)
            new_flight = read_flight.dict()
            new_flight["environment"] = env
            new_flight = Flight(**new_flight)
            async with FlightRepository() as flight_repo:
                flight_repo.fetch_flight(new_flight)
                await flight_repo.create_flight(
                    motor_kind=read_flight.rocket.motor.motor_kind,
                    rocket_option=read_flight.rocket.rocket_option,
                )
                await flight_repo.delete_flight_by_id(flight_id)
        except PyMongoError as e:
            logger.error(
                f"controllers.flight.update_env_by_flight_id: PyMongoError {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to update environment from db",
            ) from e
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.flight.update_env: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update environment: {exc_str}",
            ) from e
        else:
            return FlightUpdated(new_flight_id=new_flight.flight_id)
        finally:
            logger.info(
                f"Call to controllers.flight.update_env completed for Flight {flight_id}; Env {hash(env)}"
            )

    @classmethod
    async def update_rocket_by_flight_id(
        cls, flight_id: str, *, rocket: Rocket, rocket_option, motor_kind
    ) -> Union[FlightUpdated, HTTPException]:
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
        try:
            read_flight = await cls.get_flight_by_id(flight_id)
            updated_rocket = rocket.dict()
            updated_rocket["rocket_option"] = rocket_option
            updated_rocket["motor"]["motor_kind"] = motor_kind
            new_flight = read_flight.dict()
            new_flight["rocket"] = updated_rocket
            new_flight = Flight(**new_flight)
            async with FlightRepository() as flight_repo:
                flight_repo.fetch_flight(new_flight)
                await flight_repo.create_flight(
                    motor_kind=motor_kind, rocket_option=rocket_option
                )
                await flight_repo.delete_flight_by_id(flight_id)
        except PyMongoError as e:
            logger.error(
                f"controllers.flight.update_rocket_by_flight_id: PyMongoError {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to update rocket from db",
            ) from e
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.flight.update_rocket: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update rocket: {exc_str}",
            ) from e
        else:
            return FlightUpdated(new_flight_id=new_flight.flight_id)
        finally:
            logger.info(
                f"Call to controllers.flight.update_rocket completed for Flight {flight_id}; Rocket {hash(rocket)}"
            )

    @staticmethod
    async def delete_flight_by_id(
        flight_id: str,
    ) -> Union[FlightDeleted, HTTPException]:
        """
        Delete a models.Flight from the database.

        Args:
            flight_id: str

        Returns:
            views.FlightDeleted

        Raises:
            HTTP 404 Not Found: If the flight is not found in the database.
        """
        try:
            async with FlightRepository() as flight_repo:
                await flight_repo.delete_flight_by_id(flight_id)
        except PyMongoError as e:
            logger.error(f"controllers.flight.delete_flight: PyMongoError {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to delete flight from db",
            ) from e
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.flight.delete_flight: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete flight: {exc_str}",
            ) from e
        else:
            return FlightDeleted(deleted_flight_id=flight_id)
        finally:
            logger.info(
                f"Call to controllers.flight.delete_flight completed for Flight {flight_id}"
            )

    @classmethod
    async def simulate_flight(
        cls,
        flight_id: str,
    ) -> Union[FlightSummary, HTTPException]:
        """
        Simulate a rocket flight.

        Args:
            flight_id: str

        Returns:
            Flight summary view.

        Raises:
            HTTP 404 Not Found: If the flight does not exist in the database.
        """
        try:
            read_flight = await cls.get_flight_by_id(flight_id=flight_id)
            flight = cls.get_rocketpy_flight(read_flight)

            _initial_conditions = InitialConditions(
                initial_altitude="Attitude - e0: {:.3f} | e1: {:.3f} | e2: {:.3f} | e3: {:.3f}".format(
                    flight.e0(0), flight.e1(0), flight.e2(0), flight.e3(0)
                ),
                initial_velocity="Velocity - Vx: {:.2f} m/s | Vy: {:.2f} m/s | Vz: {:.2f} m/s".format(
                    flight.vx(0), flight.vy(0), flight.vz(0)
                ),
                initial_position="Position - x: {:.2f} m | y: {:.2f} m | z: {:.2f} m".format(
                    flight.x(0), flight.y(0), flight.z(0)
                ),
                initial_angular_position="Euler Angles - Spin φ : {:.2f}° | Nutation θ: {:.2f}° | Precession ψ: {:.2f}°".format(
                    flight.phi(0), flight.theta(0), flight.psi(0)
                ),
                initial_angular_velocity="Angular Velocity - ω1: {:.2f} rad/s | ω2: {:.2f} rad/s| ω3: {:.2f} rad/s".format(
                    flight.w1(0), flight.w2(0), flight.w3(0)
                ),
            )

            _numerical_integration_settings = NumericalIntegrationSettings(
                max_time="Maximum Allowed Flight Time: {:f} s".format(
                    flight.max_time
                ),
                max_time_step="Maximum Allowed Time Step: {:f} s".format(
                    flight.max_time_step
                ),
                min_time_step="Minimum Allowed Time Step: {:e} s".format(
                    flight.min_time_step
                ),
                relative_error_tolerance=f"Relative Error Tolerance: {flight.rtol}",
                absolute_error_tolerance=f"Absolute Error Tolerance: {flight.atol}",
                time_overshoot=f"Allow Event Overshoot: {flight.time_overshoot}",
                terminate_on_apogee=f"Terminate Simulation on Apogee: {flight.terminate_on_apogee}",
                number_of_time_steps=f"Number of Time Steps Used: {len(flight.time_steps)}",
                function_evaluations_per_time_step=f"Number of Derivative Functions Evaluation: {sum(flight.function_evaluations_per_time_step)}",
                avg_function_evaluations_per_time_step="Average Function Evaluations per Time Step: {:3f}".format(
                    sum(flight.function_evaluations_per_time_step)
                    / len(flight.time_steps)
                ),
            )

            _launch_rail_conditions = LaunchRailConditions(
                rail_length="Launch Rail Length: {:.2f} m".format(
                    flight.rail_length
                ),
                flight_inclination="Launch Rail Inclination: {:.2f}°".format(
                    flight.inclination
                ),
                flight_heading="Launch Rail Heading: {:.2f}°".format(
                    flight.heading
                ),
            )

            _surface_wind_conditions = SurfaceWindConditions(
                frontal_surface_wind_speed="Frontal Surface Wind Speed: {:.2f} m/s".format(
                    flight.frontal_surface_wind
                ),
                lateral_surface_wind_speed="Lateral Surface Wind Speed: {:.2f} m/s".format(
                    flight.lateral_surface_wind
                ),
            )

            _out_of_rail_conditions = OutOfRailConditions(
                out_of_rail_time="Rail Departure Time: {:.3f} s".format(
                    flight.out_of_rail_time
                ),
                out_of_rail_velocity="Rail Departure Velocity: {:.3f} m/s".format(
                    flight.out_of_rail_velocity
                ),
                out_of_rail_static_margin="Rail Departure Static Margin: {:.3f} c".format(
                    flight.rocket.static_margin(flight.out_of_rail_time)
                ),
                out_of_rail_angle_of_attack="Rail Departure Angle of Attack: {:.3f}°".format(
                    flight.angle_of_attack(flight.out_of_rail_time)
                ),
                out_of_rail_thrust_weight_ratio="Rail Departure Thrust-Weight Ratio: {:.3f}".format(
                    flight.rocket.thrust_to_weight(flight.out_of_rail_time)
                ),
                out_of_rail_reynolds_number="Rail Departure Reynolds Number: {:.3e}".format(
                    flight.reynolds_number(flight.out_of_rail_time)
                ),
            )

            _burnout_conditions = BurnoutConditions(
                burnout_time="Burn out time: {:.3f} s".format(
                    flight.rocket.motor.burn_out_time
                ),
                burnout_altitude="Altitude at burn out: {:.3f} m (AGL)".format(
                    flight.z(flight.rocket.motor.burn_out_time)
                    - flight.env.elevation
                ),
                burnout_rocket_velocity="Rocket velocity at burn out: {:.3f} m/s".format(
                    flight.speed(flight.rocket.motor.burn_out_time)
                ),
                burnout_freestream_velocity="Freestream velocity at burn out: {:.3f} m/s".format(
                    (
                        flight.stream_velocity_x(
                            flight.rocket.motor.burn_out_time
                        )
                        ** 2
                        + flight.stream_velocity_y(
                            flight.rocket.motor.burn_out_time
                        )
                        ** 2
                        + flight.stream_velocity_z(
                            flight.rocket.motor.burn_out_time
                        )
                        ** 2
                    )
                    ** 0.5
                ),
                burnout_mach_number="Mach Number at burn out: {:.3f}".format(
                    flight.mach_number(flight.rocket.motor.burn_out_time)
                ),
                burnout_kinetic_energy="Kinetic energy at burn out: {:.3e}".format(
                    flight.kinetic_energy(flight.rocket.motor.burn_out_time)
                ),
            )

            _apogee_conditions = ApogeeConditions(
                apogee_altitude="Apogee Altitude: {:.3f} m (ASL) | {:.3f} m (AGL)".format(
                    flight.apogee, flight.apogee - flight.env.elevation
                ),
                apogee_time="Apogee Time: {:.3f} s".format(flight.apogee_time),
                apogee_freestream_speed="Apogee Freestream Speed: {:.3f} m/s".format(
                    flight.apogee_freestream_speed
                ),
            )

            _maximum_values = MaximumValues(
                maximum_speed="Maximum Speed: {:.3f} m/s at {:.2f} s".format(
                    flight.max_speed, flight.max_speed_time
                ),
                maximum_mach_number="Maximum Mach Number: {:.3f} Mach at {:.2f} s".format(
                    flight.max_mach_number, flight.max_mach_number_time
                ),
                maximum_reynolds_number="Maximum Reynolds Number: {:.3e} at {:.2f} s".format(
                    flight.max_reynolds_number, flight.max_reynolds_number_time
                ),
                maximum_dynamic_pressure="Maximum Dynamic Pressure: {:.3e} Pa at {:.2f} s".format(
                    flight.max_dynamic_pressure,
                    flight.max_dynamic_pressure_time,
                ),
                maximum_acceleration_during_motor_burn="Maximum Acceleration During Motor Burn: {:.3f} m/s² at {:.2f} s".format(
                    flight.max_acceleration, flight.max_acceleration_time
                ),
                maximum_gs_during_motor_burn="Maximum Gs During Motor Burn: {:.3f} g at {:.2f} s".format(
                    flight.max_acceleration
                    / flight.env.gravity(
                        flight.z(flight.max_acceleration_time)
                    ),
                    flight.max_acceleration_time,
                ),
                maximum_acceleration_after_motor_burn="Maximum Acceleration After Motor Burn: {:.3f} m/s² at {:.2f} s".format(
                    flight.max_acceleration_power_off,
                    flight.max_acceleration_power_off_time,
                ),
                maximum_gs_after_motor_burn="Maximum Gs After Motor Burn: {:.3f} g at {:.2f} s".format(
                    flight.max_acceleration_power_off / flight.env.standard_g,
                    flight.max_acceleration_power_off_time,
                ),
                maximum_upper_rail_button_normal_force="Maximum Upper Rail Button Normal Force: {:.3f} N".format(
                    flight.max_rail_button1_normal_force
                ),
                maximum_upper_rail_button_shear_force="Maximum Upper Rail Button Shear Force: {:.3f} N".format(
                    flight.max_rail_button1_shear_force
                ),
                maximum_lower_rail_button_normal_force="Maximum Lower Rail Button Normal Force: {:.3f} N".format(
                    flight.max_rail_button2_normal_force
                ),
                maximum_lower_rail_button_shear_force="Maximum Lower Rail Button Shear Force: {:.3f} N".format(
                    flight.max_rail_button2_shear_force
                ),
            )

            if len(flight.impact_state) != 0:
                _impact_conditions = ImpactConditions(
                    x_impact_position="X Impact: {:.3f} m".format(
                        flight.x_impact
                    ),
                    y_impact_position="Y Impact: {:.3f} m".format(
                        flight.y_impact
                    ),
                    time_of_impact="Time of Impact: {:.3f} s".format(
                        flight.t_final
                    ),
                    impact_velocity="Velocity at Impact: {:.3f} m/s".format(
                        flight.impact_velocity
                    ),
                )
            elif flight.terminate_on_apogee is False:
                _impact_conditions = ImpactConditions(
                    time="Time: {:.3f} s".format(flight.solution[-1][0]),
                    altitude="Altitude: {:.3f} m".format(
                        flight.solution[-1][3]
                    ),
                )

            if len(flight.parachute_events) == 0:
                _events_registered = EventsRegistered(
                    events_trace="No parachute event registered"
                )
            else:
                events = {}
                for event in flight.parachute_events:
                    trigger_time = event[0]
                    parachute = event[1]
                    open_time = trigger_time + parachute.lag
                    velocity = flight.free_stream_speed(open_time)
                    altitude = flight.z(open_time)
                    name = parachute.name.title()
                    events[name] = []
                    events[name].append(
                        name
                        + " Ejection Triggered at: {:.3f} s".format(
                            trigger_time
                        )
                    )
                    events[name].append(
                        name
                        + " Parachute Inflated at: {:.3f} s".format(open_time)
                    )
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
                _events_registered = EventsRegistered(events_trace=events)

            _flight_data = FlightData(
                initial_conditions=_initial_conditions,
                numerical_integration_settings=_numerical_integration_settings,
                surface_wind_conditions=_surface_wind_conditions,
                launch_rail_conditions=_launch_rail_conditions,
                out_of_rail_conditions=_out_of_rail_conditions,
                burnout_conditions=_burnout_conditions,
                apogee_conditions=_apogee_conditions,
                maximum_values=_maximum_values,
                impact_conditions=_impact_conditions,
                events_registered=_events_registered,
            )

            flight_summary = FlightSummary(flight_data=_flight_data)
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.flight.simulate_flight: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to simulate flight: {exc_str}",
            ) from e
        else:
            return flight_summary
        finally:
            logger.info(
                f"Call to controllers.flight.simulate_flight completed for Flight {flight_id}"
            )
