from pydantic import BaseModel
from typing import Optional
from lib.models.motor import Motor
from lib.models.aerosurfaces import Fins, NoseCone, Tail, RailButtons
from lib.models.parachute import Parachute

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
