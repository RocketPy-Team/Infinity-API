from enum import Enum
from typing import Optional, Tuple, List
from pydantic import BaseModel, PrivateAttr
from lib.models.motor import Motor
from lib.models.aerosurfaces import Fins, NoseCone, Tail, RailButtons
from lib.models.parachute import Parachute


class RocketOptions(str, Enum):
    CALISTO: str = "CALISTO"
    CUSTOM: str = "CUSTOM"


class Rocket(BaseModel):
    # Required parameters
    motor: Motor = Motor()
    radius: float = 0.0632
    mass: float = 16.235
    motor_position: float = -1.255
    parachutes: Parachute = Parachute()
    center_of_mass_without_motor: int = 0
    inertia: Tuple[float, float, float] = (6.321, 6.321, 0.0346)
    rail_buttons: RailButtons = RailButtons(
        upper_button_position=-0.5,
        lower_button_position=0.2,
        angular_position=45,
    )
    nose: NoseCone = NoseCone(
        length=0.55829,
        kind="vonKarman",
        position=1.278,
        base_radius=0.0635,
        rocket_radius=0.0635,
    )
    fins: Fins = Fins(
        n=4,
        root_chord=0.12,
        tip_chord=0.04,
        span=0.1,
        position=-1.04956,
        cant_angle=0,
        radius=0.0635,
        airfoil="",
    )
    tail: Tail = Tail(
        top_radius=0.0635,
        bottom_radius=0.0435,
        length=0.06,
        position=-1.194656,
        radius=0.0635,
    )
    _rocket_option: RocketOptions = PrivateAttr(default=RocketOptions.CALISTO)

    # Optional parameters
    # TODO: implement field validation so a list of possible tailToNose values is provided in the api docs
    power_off_drag: Optional[List[Tuple[float, float]]] = [
        (0.01, 0.333865758),
        (0.02, 0.394981721),
        (0.03, 0.407756063),
    ]
    power_on_drag: Optional[List[Tuple[float, float]]] = [
        (0.01, 0.333865758),
        (0.02, 0.394981721),
        (0.03, 0.407756063),
    ]
    coordinate_system_orientation: Optional[str] = "tail_to_nose"

    @property
    def rocket_option(self) -> RocketOptions:
        return self._rocket_option

    def set_rocket_option(self, rocket_option: RocketOptions):
        self._rocket_option = rocket_option
