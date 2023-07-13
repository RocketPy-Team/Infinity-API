from rocketpy import SolidMotor
from pydantic import BaseModel, Field
from typing import Optional, Callable, List
import datetime

class Env(BaseModel, frozen=True):
    latitude: float 
    longitude: float
    railLength: Optional[float] = 5.2
    elevation: Optional[int] = 1400
    atmosphericModelType: Optional[str] = 'StandardAtmosphere' 
    atmosphericModelFile: Optional[str] = 'GFS'
    date: Optional[datetime.datetime] = datetime.datetime.today() + datetime.timedelta(days=1) 

class RailButtons(BaseModel, frozen=True):
        upper_button_position: Optional[float] = -0.5
        lower_button_position: Optional[float] = 0.2
        angularPosition: Optional[float] = 45 
    
class Motor(BaseModel, frozen=True):
    burnOut: float
    grainNumber: int
    grainDensity: float
    grainOuterRadius: float
    grainInitialInnerRadius: float
    grainInitialHeight: float
    grainsCenterOfMassPosition: float
    #TBD: thrustSource must be the id of a previously uploaded .eng file and a list of "default" files must be provided in the api docs
    thrustSource: Optional[str] = "lib/data/motors/Cesaroni_M1670.eng"
    grainSeparation: float
    nozzleRadius: float
    throatRadius: float
    interpolationMethod: str

class NoseCone(BaseModel, frozen=True):
    length: float
    kind: str
    position: float
    baseRadius: float
    rocketRadius: float

class Fins(BaseModel, frozen=True):
    n: int
    rootChord: float
    tipChord: float
    span: float
    position: float
    cantAngle: float
    radius: float
    airfoil: str

class TrapezoidalFins(Fins, frozen=True):
    def __init__():
        super().__init__()
    
class Tail(BaseModel, frozen=True):
    topRadius: float
    bottomRadius: float
    length: float
    position: float
    radius: float

class Parachute(BaseModel, frozen=True):
    name: "List[str]"
    CdS: "List[float]"
    samplingRate: "List[int]"
    lag: "List[float]"
    noise: "List[tuple[float, float, float]]"
    triggers: "List[str]"

    def __hash__(self):
        return hash((
            tuple(self.name),
            tuple(self.CdS),
            tuple(self.samplingRate),
            tuple(self.lag),
            tuple(self.noise),
            tuple(self.triggers),
        ))

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

class Rocket(BaseModel, frozen=True):
    radius: float
    mass: float
    inertiaI: float
    inertiaZ: float
    #TBD: powerOffDrag an powerOnDrag need to be the id of previously uploaded .csv files and a list of "default" files must be provided in the api docs
    powerOffDrag: Optional[str] = 'lib/data/calisto/powerOffDragCurve.csv'
    powerOnDrag: Optional[str] = 'lib/data/calisto/powerOnDragCurve.csv'
    centerOfDryMassPosition: int
    #TBD: a list of possible tailToNose values must be provided in the api docs
    coordinateSystemOrientation: Optional[str] = "tailToNose"
    motorPosition: float
    railButtons: RailButtons
    motor: Motor
    nose: NoseCone
    fins: Fins
    tail: Tail
    parachutes: Parachute

class Flight(BaseModel, frozen=True):
    environment: Env
    rocket: Rocket
    inclination: int
    heading: int
