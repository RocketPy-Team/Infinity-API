from lib.models import Rocket, Flight, Env
from lib.views import EnvView, FlightView

from rocketpy import Environment, SolidMotor, AeroSurfaces
import rocketpy.Flight
import rocketpy.Rocket
import rocketpy.Parachute

#improve semantics

class EnvController():
    def __init__(self, env: Env, default: bool = True):
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

class FlightController():
    def __init__(self, flight: Flight, default: bool = True):
        rocketpy_flight = rocketpy.Flight(
                rocket = Rocket(),
                inclination=flight.inclination, 
                heading=flight.heading,
                environment= EnvController(flight.environment).rocketpy_env
        )
        self.rocketpy_flight = rocketpy_flight 

    def summary(self, level: str):
        flight_view = FlightView(self.rocketpy_flight)
        if level == 'full':
            return flight_view.full_flight_summary()

class RocketController():
    def __init__(self, rocket: Rocket, default: bool = True):
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
        # railButtons = rocket.RailButtons()
        self.rocketpy_rocket.setRailButtons(rocket.RailButtons.distanceToCm,
                                            rocket.RailButtons.angularPosition)
        self.rocketpy_rocket.addMotor(MotorController(rocket.motor).rocketpy_motor, 
                                      rocket.motorPosition)

        nose = NoseConeController(rocket.Nose()).rocketpy_nose
        self.rocketpy_rocket.aerodynamicSurfaces.append(aeroSurface=nose, position=nose.position)
        self.rocketpy_rocket.nose.append(nose)
        self.rocketpy_rocket.evaluateStaticMargin()

        finset = TrapezoidalFinsController(rocket.Fins()).rocketpy_finset
        self,rocketpy_rocket.aerodynamicSurfaces.append(aeroSurface=finset, position=finset.position)
        self.rocketpy_rocket.fins.append(finset)
        self.rocketpy_rocket.evaluateStaticMargin()

        tail = TailController(rocket.Tail()).rocketpy_tail 
        self.rocketpy_rocket.aerodynamicSurfaces.append(aeroSurface=tail, position=tail.position)
        self.rocketpy_rocket.tail.append(tail)
        self.rocketpy_rocket.evaluateStaticMargin()

        rocket_parachutes = rocket.Parachute()
        for p in range(len(rocket_parachutes.name)):
            parachute = ParachuteController(rocket_parachutes, p).rocketpy_parachute
            self.rocketpy_rocket.append(parachute)

        self.rocketpy_rocket = rocketpy_rocket 

    class NoseConeController():
        def __init__(self, nose: Rocket.Nose, default: bool = True):
            rocketpy_nose = NoseCone(
                    length=nose.length,
                    kind=nose.kind,
                    baseRadius=rocket.radius,
                    rocketRadius=rocket.radius
            )
            rocketpy_nose.position = nose.position
            self.rocketpy_nose = rocketpy_nose

    class TrapezoidalFinsController():
        def __init__(self, trapezoidalFins: Rocket.Fins, default: bool = True):
            rocketpy_finset = TrapezoidalFins(
                    n=trapezoidalFins.n,
                    rootChord=trapezoidalFins.rootChord,
                    tipChord=trapezoidalFins.tipChord,
                    span=trapezoidalFins.span,
                    cantAngle=trapezoidalFins.cantAngle,
                    radius=trapezoidalFins.radius,
                    airfoil=trapezoidalFins.airfoil
            )
            rocketpy_finset.position = trapezoidalFins.position,
            self.rocketpy_finset = rocketpy_finset

    class TailController():
        def __init__(self, tail: Rocket.Tail, default: bool = True):
            rocketpy_tail = rocketpy.Tail(
                    topRadius=tail.topRadius,
                    bottomRadius=tail.bottomRadius,
                    length=tail.length,
                    position=tail.position
            )
            rocketpy_tail.position = tail.position
            self.rocketpy_tail = rocketpy_tail

    class ParachuteController():
        def __init__(self, parachute: Rocket.Parachute, p: int, default: bool = True):
            rocketpy_parachute = rocketpy.Parachute(
                    name=parachute[p].name,
                    CdS=parachute[p].CdS,
                    trigger=parachute[p].trigger,
                    samplingRate=parachute[p].samplingRate,
                    lag=parachute[p].lag,
                    noise=parachute[p].noise
            )
            self.rocketpy_parachute = rocketpy_parachute

class MotorController():
    def __init__(self, motor: Rocket.Motor, default: bool = True):
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
