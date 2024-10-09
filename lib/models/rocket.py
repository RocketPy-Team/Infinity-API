from enum import Enum
from typing import Optional, Tuple, List, Union
from pydantic import BaseModel
from lib.models.motor import Motor
from lib.models.aerosurfaces import (
    Fins,
    NoseCone,
    Tail,
    RailButtons,
)


class CoordinateSystemOrientation(str, Enum):
    TAIL_TO_NOSE: str = "TAIL_TO_NOSE"
    NOSE_TO_TAIL: str = "NOSE_TO_TAIL"


class Parachute(BaseModel):
    name: str
    cd_s: float
    sampling_rate: int
    lag: float
    trigger: Union[str, float]
    noise: Tuple[float, float, float]


class Rocket(BaseModel):
    # Required parameters
    motor: Motor
    radius: float
    mass: float
    motor_position: float
    center_of_mass_without_motor: int
    inertia: Tuple[float, float, float]
    power_off_drag: List[Tuple[float, float]]
    power_on_drag: List[Tuple[float, float]]

    # Optional parameters
    parachutes: Optional[List[Parachute]] = None
    rail_buttons: Optional[RailButtons] = None
    nose: Optional[NoseCone] = None
    fins: Optional[List[Fins]] = None
    tail: Optional[Tail] = None
    coordinate_system_orientation: Optional[CoordinateSystemOrientation] = None
