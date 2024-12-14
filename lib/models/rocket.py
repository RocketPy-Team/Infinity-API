from enum import Enum
from typing import Optional, Tuple, List, Union
from pydantic import BaseModel
from lib.models.motor import Motor
from lib.models.aerosurfaces import (
    Fins,
    NoseCone,
    Tail,
    RailButtons,
    Parachute,
)


class CoordinateSystemOrientation(str, Enum):
    TAIL_TO_NOSE: str = "TAIL_TO_NOSE"
    NOSE_TO_TAIL: str = "NOSE_TO_TAIL"


class Rocket(BaseModel):

    # Required parameters
    motor: Motor
    radius: float
    mass: float
    motor_position: float
    center_of_mass_without_motor: int
    inertia: Union[
        Tuple[float, float, float],
        Tuple[float, float, float, float, float, float],
    ] = (0, 0, 0)
    power_off_drag: List[Tuple[float, float]] = [(0, 0)]
    power_on_drag: List[Tuple[float, float]] = [(0, 0)]
    coordinate_system_orientation: CoordinateSystemOrientation = (
        CoordinateSystemOrientation.TAIL_TO_NOSE
    )

    # Optional parameters
    parachutes: Optional[List[Parachute]] = None
    rail_buttons: Optional[RailButtons] = None
    nose: Optional[NoseCone] = None
    fins: Optional[List[Fins]] = None
    tail: Optional[Tail] = None
