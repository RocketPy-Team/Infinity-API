from lib.models import Rocket, Flight, Env, NoseCone, TrapezoidalFins, Tail, Parachute, Motor, RailButtons
from lib.views import FlightSummary, SurfaceWindConditions, RailDepartureState, BurnoutState, Apogee, MaximumValues
from lib.repositories.flight import FlightRepository 

from rocketpy import Environment, SolidMotor
from rocketpy.AeroSurface import NoseCone as rocketpy_NoseCone
from rocketpy.AeroSurface import TrapezoidalFins as rocketpy_TrapezoidalFins
from rocketpy.AeroSurface import Tail as rocketpy_Tail

from typing import Dict, Any, Union
from fastapi import Response, status

import ast
import rocketpy.Flight
import rocketpy.Rocket
import rocketpy.Parachute

class EnvController(): 
    """ 
    Controller for the Environment model.

    Init Attributes:
        env (models.Env): Environment model object.

    Enables:
        - Create a rocketpy.Environment object from an Env model object.
    """
    def __init__(self, env: Env):
        rocketpy_env = Environment(
                railLength=env.railLength,
                latitude=env.latitude,
                longitude=env.longitude,
                elevation=env.elevation,
                date=env.date
        )
        rocketpy_env.setAtmosphericModel(
                type=env.atmosphericModelType, 
                file=env.atmosphericModelFile
        )
        self.rocketpy_env = rocketpy_env 
        self.env = env


class RocketController():
    """
    Controller for the Rocket model.

    Init Attributes:
        rocket (models.Rocket): Rocket model object.

    Enables:
       create a rocketpy.Rocket object from a Rocket model object.
    """
    def __init__(self, rocket: Rocket):
        rocketpy_rocket = rocketpy.Rocket(
                radius=rocket.radius,
                mass=rocket.mass,
                inertiaI=rocket.inertiaI,
                inertiaZ=rocket.inertiaZ,
                powerOffDrag=rocket.powerOffDrag,
                powerOnDrag=rocket.powerOnDrag,
                centerOfDryMassPosition=rocket.centerOfDryMassPosition,
                coordinateSystemOrientation=rocket.coordinateSystemOrientation
        )

        #RailButtons
        rocketpy_rocket.setRailButtons(upper_button_position=rocket.railButtons.upper_button_position,
                                       lower_button_position=rocket.railButtons.lower_button_position,
                                       angular_position=rocket.railButtons.angularPosition)
        rocketpy_rocket.addMotor(MotorController(rocket.motor).rocketpy_motor,
                                 rocket.motorPosition)

        #NoseCone
        nose = self.NoseConeController(rocket.nose).rocketpy_nose
        rocketpy_rocket.aerodynamicSurfaces.add(nose, nose.position)
        rocketpy_rocket.evaluateStaticMargin()

        #FinSet
        #TBD: re-write this to match overall fins not only TrapezoidalFins
        finset = self.TrapezoidalFinsController(rocket.fins).rocketpy_finset
        rocketpy_rocket.aerodynamicSurfaces.add(finset, finset.position)
        rocketpy_rocket.evaluateStaticMargin()

        #Tail
        tail = self.TailController(rocket.tail).rocketpy_tail 
        rocketpy_rocket.aerodynamicSurfaces.add(tail, tail.position)
        rocketpy_rocket.evaluateStaticMargin()

        #Parachutes
        for p in range(len(rocket.parachutes)):
            parachute_trigger = rocket.parachutes[p].triggers[0]
            if self.ParachuteController.check_trigger(parachute_trigger):
                rocket.parachutes[p].triggers[0] = compile(parachute_trigger, '<string>', 'eval')
                parachute = self.ParachuteController(rocket.parachutes, p).rocketpy_parachute
                rocketpy_rocket.parachutes.append(parachute)
            else:
                print("Parachute trigger not valid. Skipping parachute.")
                continue
            
        self.rocketpy_rocket = rocketpy_rocket 
        self.rocket = rocket

    class NoseConeController():
        """
        Controller for the NoseCone model.

        Init Attributes:
            nose (models.NoseCone): NoseCone model object.

        Enables:
            - Create a rocketpy.AeroSurface.NoseCone object from a NoseCone model object.
        """
        def __init__(self, nose: NoseCone):
            rocketpy_nose = rocketpy_NoseCone(
                    length=nose.length,
                    kind=nose.kind,
                    baseRadius=nose.baseRadius,
                    rocketRadius=nose.rocketRadius
            )
            rocketpy_nose.position = nose.position
            self.rocketpy_nose = rocketpy_nose
            self.nose = nose

    class TrapezoidalFinsController():
        """
        Controller for the TrapezoidalFins model.

        Init Attributes:
            trapezoidalFins (models.TrapezoidalFins): TrapezoidalFins model object.

        Enables:
            - Create a rocketpy.AeroSurface.TrapezoidalFins object from a TrapezoidalFins model object.
        """
        def __init__(self, trapezoidalFins: TrapezoidalFins):
            rocketpy_finset = rocketpy_TrapezoidalFins(
                    n=trapezoidalFins.n,
                    rootChord=trapezoidalFins.rootChord,
                    tipChord=trapezoidalFins.tipChord,
                    span=trapezoidalFins.span,
                    cantAngle=trapezoidalFins.cantAngle,
                    rocketRadius=trapezoidalFins.radius,
                    airfoil=trapezoidalFins.airfoil
            )
            rocketpy_finset.position = trapezoidalFins.position
            self.rocketpy_finset = rocketpy_finset
            self.trapezoidalFins = trapezoidalFins

    class TailController():
        """
        Controller for the Tail model.

        Init Attributes:
            tail (models.Tail): Tail model object.

        Enables:
            - Create a rocketpy.AeroSurface.Tail object from a Tail model object.
        """
        def __init__(self, tail: Tail):
            rocketpy_tail = rocketpy_Tail(
                    topRadius=tail.topRadius,
                    bottomRadius=tail.bottomRadius,
                    length=tail.length,
                    rocketRadius=tail.radius
            )
            rocketpy_tail.position = tail.position
            self.rocketpy_tail = rocketpy_tail
            self.tail = tail

    class ParachuteController():
        """
        Controller for the Parachute model.

        Init Attributes:
            parachute (models.Parachute): Parachute model object.

        Enables:
            - Create a rocketpy.Parachute.Parachute object from a Parachute model object.
        """
        def __init__(self, parachute: Parachute, p: int):
            rocketpy_parachute = rocketpy.Parachute.Parachute(
                    name=parachute[p].name[0],
                    CdS=parachute[p].CdS[0],
                    trigger=eval(parachute[p].triggers[0]),
                    samplingRate=parachute[p].samplingRate[0],
                    lag=parachute[p].lag[0],
                    noise=parachute[p].noise[0]
            )
            self.rocketpy_parachute = rocketpy_parachute
            self.parachute = parachute

        def check_trigger(expression: str) -> bool:
            """
            Check if the trigger expression is valid.

            Args:
                expression (str): Trigger expression.

            Returns:
                bool: True if the expression is valid, False otherwise.
            """

            # Parsing the expression into an AST
            try:
                parsed_expression = ast.parse(expression, mode='eval')
            except SyntaxError:
                print("Invalid syntax.")
                return False

            # Constant case (supported after beta v1) 
            if isinstance(parsed_expression.body, ast.Constant):
                return True
            # Name case (supported after beta v1)
            elif isinstance(parsed_expression.body, ast.Name) \
            and parsed_expression.body.id == "apogee":
                global apogee
                apogee = "apogee"
                return True

            # Validating the expression structure
            if not isinstance(parsed_expression.body, ast.Lambda):
                print("Invalid expression structure (not a Lambda).")
                return False

            lambda_node = parsed_expression.body
            if len(lambda_node.args.args) != 3:
                print("Invalid expression structure (invalid arity).")
                return False

            if not isinstance(lambda_node.body, ast.Compare):
                try:
                    for operand in lambda_node.body.values:
                        if not isinstance(operand, ast.Compare):
                            print("Invalid expression structure (not a Compare).")
                            return False
                except AttributeError:
                    print("Invalid expression structure (not a Compare).")
                    return False

            # Restricting access to functions or attributes
            for node in ast.walk(lambda_node):
                if isinstance(node, ast.Call):
                    print("Calling functions is not allowed in the expression.")
                    return False
                elif isinstance(node, ast.Attribute):
                    print("Accessing attributes is not allowed in the expression.")
                    return False
            return True 

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

    def simulate(flight_id: int):
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
        successfully_created_flight = flight.create_flight(self.rocketpy_flight)
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

    def get_rocketpy_flight(flight_id: int) -> str:
        """
        Get a rocketpy flight object encoded as jsonpickle string from the database.

        Args:
            flight_id (int): Flight id.

        Returns:
            str: jsonpickle string of the rocketpy flight.

        Raises:
            HTTP 404 Not Found: If the flight is not found in the database.
        """
        successfully_read_rocketpy_flight = FlightRepository(flight_id=flight_id).get_rocketpy_flight()
        if not successfully_read_rocketpy_flight:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
        return { "jsonpickle_rocketpy_flight": successfully_read_rocketpy_flight }
           
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

class MotorController():
    """
    Controller for the motor model.

    Init Attributes:
        motor (models.Motor): Motor model object.

    Enables:
        - Create a rocketpy.Motor object from a Motor model object.
    """
    def __init__(self, motor: Motor):
        rocketpy_motor = SolidMotor(
                burnOut=motor.burnOut,
                grainNumber=motor.grainNumber,
                grainDensity=motor.grainDensity,
                grainOuterRadius=motor.grainOuterRadius,
                grainInitialInnerRadius=motor.grainInitialInnerRadius,
                grainInitialHeight=motor.grainInitialHeight,
                grainsCenterOfMassPosition=-motor.grainsCenterOfMassPosition,
                thrustSource=motor.thrustSource
        )
        rocketpy_motor.grainSeparation = motor.grainSeparation
        rocketpy_motor.nozzleRadius = motor.nozzleRadius
        rocketpy_motor.throatRadius = motor.throatRadius
        rocketpy_motor.interpolationMethod = motor.interpolationMethod
        self.rocketpy_motor = rocketpy_motor
        self.motor = motor 
