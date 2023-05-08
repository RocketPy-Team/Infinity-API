from lib.models import Rocket, Flight, Env, NoseCone, TrapezoidalFins, Tail, Parachute, Motor, RailButtons
from lib.views import EnvView, FlightView

from rocketpy import Environment, SolidMotor, AeroSurfaces
import rocketpy.Flight
import rocketpy.Rocket
import rocketpy.Parachute

class EnvController():
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


class RocketController():
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
        rocketpy_rocket.setRailButtons(rocket.railButtons.distanceToCM,
                                       rocket.railButtons.angularPosition)
        rocketpy_rocket.addMotor(MotorController(rocket.motor).rocketpy_motor,
                                 rocket.motorPosition)

        #NoseCone
        nose = self.NoseConeController(rocket.nose).rocketpy_nose
        rocketpy_rocket.aerodynamicSurfaces.append(aeroSurface=nose, position=nose.position)
        rocketpy_rocket.nosecone.append(nose)
        rocketpy_rocket.evaluateStaticMargin()

        #FinSet
        #TBD: re-write this to match overall fins not only TrapezoidalFins
        finset = self.TrapezoidalFinsController(rocket.fins).rocketpy_finset
        rocketpy_rocket.aerodynamicSurfaces.append(aeroSurface=finset, position=finset.position)
        rocketpy_rocket.fins.append(finset)
        rocketpy_rocket.evaluateStaticMargin()

        #Tail
        tail = self.TailController(rocket.tail).rocketpy_tail 
        rocketpy_rocket.aerodynamicSurfaces.append(aeroSurface=tail, position=tail.position)
        rocketpy_rocket.tail.append(tail)
        rocketpy_rocket.evaluateStaticMargin()

        #Parachutes
        for p in range(len(rocket.parachutes)):
            parachute = self.ParachuteController(rocket.parachutes, p).rocketpy_parachute
            rocketpy_rocket.parachutes.append(parachute)

        self.rocketpy_rocket = rocketpy_rocket 

    class NoseConeController():
        def __init__(self, nose: NoseCone):
            rocketpy_nose = AeroSurfaces.NoseCone(
                    length=nose.length,
                    kind=nose.kind,
                    baseRadius=nose.baseRadius,
                    rocketRadius=nose.rocketRadius
            )
            rocketpy_nose.position = nose.position
            self.rocketpy_nose = rocketpy_nose

    class TrapezoidalFinsController():
        def __init__(self, trapezoidalFins: TrapezoidalFins):
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
        def __init__(self, tail: Tail):
            rocketpy_tail = AeroSurfaces.Tail(
                    topRadius=tail.topRadius,
                    bottomRadius=tail.bottomRadius,
                    length=tail.length,
                    rocketRadius=tail.radius
            )
            rocketpy_tail.position = tail.position
            self.rocketpy_tail = rocketpy_tail

    class ParachuteController():
        def __init__(self, parachute: Parachute, p: int):
            rocketpy_parachute = rocketpy.Parachute.Parachute(
                    name=parachute[p].name[0],
                    CdS=parachute[p].CdS[0],
                    Trigger=parachute[p].triggers[0],
                    samplingRate=parachute[p].samplingRate[0],
                    lag=parachute[p].lag[0],
                    noise=parachute[p].noise[0]
            )
            self.rocketpy_parachute = rocketpy_parachute

class FlightController():
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

    def summary(self, level: str):
        flight_view = FlightView(self.rocketpy_flight)
        if level == 'full':
            return flight_view.full_flight_summary()


class MotorController():
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
