from lib.models import Rocket, Flight, Env, NoseCone, TrapezoidalFins, Tail, Parachute, Motor, RailButtons
from lib.views import EnvView, FlightView

from rocketpy import Environment, SolidMotor, AeroSurfaces
import rocketpy.Flight
import rocketpy.Rocket
import rocketpy.Parachute

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
                rocket = RocketController(flight.rocket).rocketpy_rocket,
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
        railButtons = RailButtons()
        rocketpy_rocket.setRailButtons(railButtons.distanceToCM,
                                       railButtons.angularPosition)

        rocketpy_rocket.addMotor(MotorController(rocket.motor).rocketpy_motor,
                                 rocket.motorPosition)

        nose = self.NoseConeController(NoseCone(rocket.radius)).rocketpy_nose
        rocketpy_rocket.aerodynamicSurfaces.append(aeroSurface=nose, position=nose.position)
        rocketpy_rocket.nosecone.append(nose)
        rocketpy_rocket.evaluateStaticMargin()

        finset = self.TrapezoidalFinsController(TrapezoidalFins(rocket.radius)).rocketpy_finset
        rocketpy_rocket.aerodynamicSurfaces.append(aeroSurface=finset, position=finset.position)
        rocketpy_rocket.fins.append(finset)
        rocketpy_rocket.evaluateStaticMargin()

        tail = self.TailController(Tail(rocket.radius)).rocketpy_tail 
        rocketpy_rocket.aerodynamicSurfaces.append(aeroSurface=tail, position=tail.position)
        rocketpy_rocket.tail.append(tail)
        rocketpy_rocket.evaluateStaticMargin()

        rocket_parachutes = Parachute(rocket.parachute_triggers)
        for p in range(len(rocket_parachutes)):
            parachute = self.ParachuteController(rocket_parachutes, p).rocketpy_parachute
            rocketpy_rocket.parachutes.append(parachute)

        self.rocketpy_rocket = rocketpy_rocket 

    class NoseConeController():
        def __init__(self, nose: NoseCone, default: bool = True):
            rocketpy_nose = AeroSurfaces.NoseCone(
                    length=nose.length,
                    kind=nose.kind,
                    baseRadius=nose.baseRadius,
                    rocketRadius=nose.rocketRadius
            )
            rocketpy_nose.position = nose.position
            self.rocketpy_nose = rocketpy_nose

    class TrapezoidalFinsController():
        def __init__(self, trapezoidalFins: TrapezoidalFins, default: bool = True):
            rocketpy_finset = AeroSurfaces.TrapezoidalFins(
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

    class TailController():
        def __init__(self, tail: Tail, default: bool = True):
            rocketpy_tail = AeroSurfaces.Tail(
                    topRadius=tail.topRadius,
                    bottomRadius=tail.bottomRadius,
                    length=tail.length,
                    rocketRadius=tail.radius
            )
            rocketpy_tail.position = tail.position
            self.rocketpy_tail = rocketpy_tail

    class ParachuteController():
        def __init__(self, parachute: Parachute, p: int, default: bool = True):
            rocketpy_parachute = rocketpy.Parachute.Parachute(
                    name=parachute[p].name[0],
                    CdS=parachute[p].CdS[0],
                    Trigger=parachute[p].trigger[0],
                    samplingRate=parachute[p].samplingRate[0],
                    lag=parachute[p].lag[0],
                    noise=parachute[p].noise[0]
            )
            self.rocketpy_parachute = rocketpy_parachute

class MotorController():
    def __init__(self, motor: Motor, default: bool = True):
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
