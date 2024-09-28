from enum import Enum
from typing import Optional, Tuple, List, Union
from pydantic import BaseModel
from lib.models.motor import Motor
from lib.models.aerosurfaces import (
    Fins,
    NoseCone,
    Tail,
    RailButtons,
    FinsKinds,
)


class CoordinateSystemOrientation(str, Enum):
    TAIL_TO_NOSE: str = "TAIL_TO_NOSE"
    NOSE_TO_TAIL: str = "NOSE_TO_TAIL"


class Parachute(BaseModel):
    name: str = "Main"
    cd_s: float = 10
    sampling_rate: int = 105
    lag: float = 1.5
    trigger: Union[str, float] = "apogee"
    noise: Tuple[float, float, float] = (0, 8.3, 0.5)


class Rocket(BaseModel):
    # Required parameters
    motor: Motor = Motor()
    radius: float = 0.0632
    mass: float = 16.235
    motor_position: float = -1.255
    center_of_mass_without_motor: int = 0
    inertia: Tuple[float, float, float] = (6.321, 6.321, 0.0346)
    power_off_drag: List[Tuple[float, float]] = [
        (0.0, 0.0),
        (0.1, 0.1),
        (0.2, 0.2),
    ]
    power_on_drag: List[Tuple[float, float]] = [
        (0.0, 0.0),
        (0.1, 0.1),
        (0.2, 0.2),
    ]

    # Optional parameters
    parachutes: Optional[List[Parachute]] = [Parachute()]
    rail_buttons: Optional[RailButtons] = RailButtons(
        name="RailButtons",
        upper_button_position=-0.5,
        lower_button_position=0.2,
        angular_position=45,
    )
    nose: Optional[NoseCone] = NoseCone(
        name="Nose",
        length=0.55829,
        kind="vonKarman",
        position=1.278,
        base_radius=0.0635,
        rocket_radius=0.0635,
    )
    fins: Optional[Fins] = Fins(
        fins_kind=FinsKinds.TRAPEZOIDAL,
        name="Fins",
        n=4,
        root_chord=0.12,
        tip_chord=0.04,
        span=0.1,
        position=-1.04956,
        cant_angle=0,
        radius=0.0635,
        airfoil="",
    )
    tail: Optional[Tail] = Tail(
        name="Tail",
        top_radius=0.0635,
        bottom_radius=0.0435,
        length=0.06,
        position=-1.194656,
        radius=0.0635,
    )
    coordinate_system_orientation: Optional[CoordinateSystemOrientation] = (
        CoordinateSystemOrientation.TAIL_TO_NOSE
    )
