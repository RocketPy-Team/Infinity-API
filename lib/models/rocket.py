from enum import Enum
from typing import Optional, Tuple, List
from pydantic import BaseModel, PrivateAttr
from lib.models.motor import Motor
from lib.models.aerosurfaces import Fins, NoseCone, Tail, RailButtons
from lib.models.parachute import Parachute


class RocketOptions(str, Enum):
    CALISTO: str = "Calisto"
    CUSTOM: str = "Custom"


class Rocket(BaseModel, frozen=True):
    # Required parameters
    rail_buttons: RailButtons = RailButtons()
    motor: Motor = Motor()
    nose: NoseCone = NoseCone()
    fins: Fins = Fins()
    tail: Tail = Tail()
    parachutes: Parachute = Parachute()
    inertia: "Tuple[float, float, float]" = (6.321, 6.321, 0.0346)
    center_of_mass_without_motor: int = 0
    radius: float = 0.0632
    mass: float = 16.235
    motor_position: float = -1.255
    power_off_drag: "List[Tuple[float, float]]" = [
        (0.01, 0.333865758),
        (0.02, 0.394981721),
        (0.03, 0.407756063),
    ]
    power_on_drag: "List[Tuple[float, float]]" = [
        (0.01, 0.333865758),
        (0.02, 0.394981721),
        (0.03, 0.407756063),
    ]
    _rocket_option: RocketOptions = PrivateAttr()

    # Optional parameters
    # TODO: a list of possible tailToNose values must be provided in the api docs
    coordinate_system_orientation: Optional[str] = "tail_to_nose"

    def __init__(self, rocket_option=RocketOptions.CALISTO, **kwargs):
        super().__init__(**kwargs)
        self._rocket_option = rocket_option

    def __hash__(self):
        temp = vars(self)
        temp = str(temp)
        return hash(temp)
