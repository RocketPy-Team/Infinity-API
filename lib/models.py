from rocketpy import SolidMotor
from pydantic import BaseModel 
from typing import Optional, List, Callable
import datetime

class Env(BaseModel):
    latitude: float 
    longitude: float
    railLength: Optional[float] = 5.2
    elevation: Optional[int] = 1400
    atmosphericModelType: Optional[str] = 'StandardAtmosphere' 
    atmosphericModelFile: Optional[str] = 'GFS'
    date: Optional[datetime.datetime] = datetime.datetime.today() + datetime.timedelta(days=1) 


class Rocket(BaseModel):
    radius: Optional[float] = 127/2000
    mass: Optional[float] = 19.197-2.956
    inertiaI: Optional[float] = 6.60
    inertiaZ: Optional[float] = 0.0351
    powerOffDrag: Optional[str] = 'lib/data/calisto/powerOffDragCurve.csv'
    powerOnDrag: Optional[str] = 'lib/data/calisto/powerOnDragCurve.csv'
    centerOfDryMassPosition: Optional[int] = 0
    coordinateSystemOrientation: Optional[str] = "tailToNose"
    motorPosition: Optional[float] = -1.255
    
    class RailButtons(BaseModel):
        distanceToCM: Optional[float] = 0.2
        angularPosition: Optional[float] = -0.5

    class Motor(BaseModel):
        burnOut: Optional[float] = 3.9
        grainNumber: Optional[int] = 5
        grainDensity: Optional[float] = 1815
        grainOuterRadius: Optional[float] = 33/1000
        grainInitialInnerRadius: Optional[float] = 15/1000
        grainInitialHeight: Optional[float] = 120/1000
        grainsCenterOfMassPosition: Optional[float] = -0.85704
        thrustSource: Optional[str] = "lib/data/motors/Cesaroni_M1670.eng"
        grainSeparation: Optional[float] = 5/1000
        nozzleRadius: Optional[float] = 33/1000
        throatRadius: Optional[float] = 11/1000
        interpolationMethod: Optional[str] = 'linear'

    class Nose(BaseModel):
        length: Optional[float] = 0.55829
        kind: Optional[str] = "vonKarman"
        position: Optional[float] = 0.71971 + 0.55829

    class Fins(BaseModel):
        class TrapezoidalFins(BaseModel):
            n: Optional[int] = 4
            rootChord: Optional[float] = 0.120
            tipChord: Optional[float] = 0.040
            span: Optional[float] = 0.100
            position: Optional[float] = -1.04956
            cantAngle: Optional[float] = 0
            radius: Optional[float] = None
            airfoil: Optional[str] = None

    class Tail(BaseModel):
        topRadius: Optional[float] = 0.0635
        bottomRadius: Optional[float] = 0.0435
        length: Optional[float] = 0.060
        position: Optional[float] = -1.194656

    class Parachute(BaseModel):
        name: Optional[str] = ['Main', 'Drogue']
        CdS: Optional[float] = [10.0, 1.0]
        trigger: Optional[List[Callable[[list, list], bool]]] = [
                lambda p, y: y[5] < 0 and y[2] < 800,
                lambda p, y: y[5] < 0
        ]
        samplingRate: Optional[float] = [105, 105]
        lag: Optional[float] = [1.5, 1.5]
        noise: Optional[float] = [(0, 8.3, 0.5), (0, 8.3, 0.5)]

    railButtons: Optional[RailButtons] = RailButtons()
    motor: Optional[Motor] = Motor()
    nose: Optional[Nose] = Nose()
    fins: Optional[Fins] = Fins.TrapezoidalFins()
    tail: Optional[Tail] = Tail()
    parachutes: Optional[Parachute] = Parachute()

class Flight(BaseModel):
    environment: Env
    rocket: Optional[Rocket] = Rocket()
    inclination: Optional[int] = 85
    heading: Optional[int] = 0

