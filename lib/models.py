from rocketpy import SolidMotor
from pydantic import BaseModel 
from typing import Optional, List, Callable, Tuple
import datetime

class Env(BaseModel):
    latitude: float 
    longitude: float
    railLength: Optional[float] = 5.2
    elevation: Optional[int] = 1400
    atmosphericModelType: Optional[str] = 'StandardAtmosphere' 
    atmosphericModelFile: Optional[str] = 'GFS'
    date: Optional[datetime.datetime] = datetime.datetime.today() + datetime.timedelta(days=1) 

class RailButtons(BaseModel):
        distanceToCM: Optional[List[float]] = [0.2, -0.5]
        angularPosition: Optional[float] = 45 
    
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

class NoseCone(BaseModel):
    length: Optional[float] = 0.55829
    kind: Optional[str] = "vonKarman"
    position: Optional[float] = 0.71971 + 0.55829
    baseRadius: Optional[float] = 0 
    rocketRadius: Optional[float] = 0 

    def __init__(self, radius: float):
        super().__init__()
        if self.baseRadius == 0:
            self.baseRadius = radius
        if self.rocketRadius == 0:
            self.rocketRadius = radius

class Fins(BaseModel):
    pass

class TrapezoidalFins(BaseModel):
    n: Optional[int] = 4
    rootChord: Optional[float] = 0.120
    tipChord: Optional[float] = 0.040
    span: Optional[float] = 0.100
    position: Optional[float] = -1.04956
    cantAngle: Optional[float] = 0
    radius: Optional[float] = 0
    airfoil: Optional[str] = "" 

    def __init__(self, radius: float):
        super().__init__()
        if self.radius == 0: 
            self.radius = radius

class Tail(BaseModel):
    topRadius: Optional[float] = 0.0635
    bottomRadius: Optional[float] = 0.0435
    length: Optional[float] = 0.060
    position: Optional[float] = -1.194656
    radius: Optional[float] = 0 

    def __init__(self, radius: float):
        super().__init__()
        if self.radius == 0:
            self.radius = radius

class Parachute(BaseModel):
    name: Optional[List[str]] = ['Main', 'Drogue']
    CdS: Optional[List[float]] = [10.0, 1.0]
    samplingRate: Optional[List[int]] = [105, 105]
    lag: Optional[List[float]] = [1.5, 1.5]
    noise: Optional[List[Tuple[float, float, float]]] = [(0.0, 8.3, 0.5), (0.0, 8.3, 0.5)]
    triggers: Optional[List[Callable]]

    def __init__(self, triggers: List[Callable] = 
                 [ lambda p, y: y[5] < 0 and y[2] < 800, lambda p, y: y[5] < 0],
                 name=name, CdS=CdS, samplingRate=samplingRate, lag=lag, noise=noise):
        super().__init__()
        if not self.triggers:
            self.triggers = triggers

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            return [self[i] for i in range(*idx.indices(len(self)))]
        else:
            return Parachute(
                name=[self.name[idx]],
                CdS=[self.CdS[idx]],
                triggers=[self.triggers[idx]],
                samplingRate=[self.samplingRate[idx]],
                lag=[self.lag[idx]],
                noise=[self.noise[idx]],
            )

    def __len__(self):
        if self.name is not None:
            return len(self.name)
        return 0

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
    railButtons: Optional[RailButtons] = RailButtons()
    motor: Optional[Motor] = Motor()
    nose: Optional[NoseCone] = NoseCone(radius)
    fins: Optional[Fins] = TrapezoidalFins(radius)
    tail: Optional[Tail] = Tail(radius)
    parachutes: Optional[Parachute] = Parachute()

class Flight(BaseModel):
    environment: Env
    rocket: Optional[Rocket] = Rocket()
    inclination: Optional[int] = 85
    heading: Optional[int] = 0

