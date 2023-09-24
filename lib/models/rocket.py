from typing import Optional, Tuple
from pydantic import BaseModel
from lib.models.motor import Motor
from lib.models.aerosurfaces import Fins, NoseCone, Tail, RailButtons
from lib.models.parachute import Parachute

class Rocket(BaseModel, frozen=True):
    radius: float
    mass: float
    inertia: "Tuple[float, float, float]" = (6.321, 6.321, 0.0346)
    #TBD: powerOffDrag an powerOnDrag need to be the id of previously uploaded .csv files and a list of "default" files must be provided in the api docs
    power_off_drag: Optional[str] = 'calisto'
    power_on_drag: Optional[str] = 'calisto'
    center_of_mass_without_motor: int
    #TBD: a list of possible tailToNose values must be provided in the api docs
    coordinate_system_orientation: Optional[str] = "tail_to_nose"
    motor_position: float
    rail_buttons: RailButtons
    motor: Motor
    nose: NoseCone
    fins: Fins
    tail: Tail
    parachutes: Parachute
