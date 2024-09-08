from enum import Enum
from pydantic import BaseModel


class RailButtons(BaseModel):
    name: str
    upper_button_position: float
    lower_button_position: float
    angular_position: float


class NoseCone(BaseModel):
    name: str
    length: float
    kind: str
    position: float
    base_radius: float
    rocket_radius: float


class FinsKinds(str, Enum):
    TRAPEZOIDAL: str = "TRAPEZOIDAL"
    ELLIPTICAL: str = "ELLIPTICAL"


class Fins(BaseModel):
    fins_kind: FinsKinds
    name: str
    n: int
    root_chord: float
    tip_chord: float
    span: float
    position: float
    cant_angle: float
    radius: float
    airfoil: str


# TODO: implement airbrakes
class AirBrakes(BaseModel):
    name: str


class Tail(BaseModel):
    name: str
    top_radius: float
    bottom_radius: float
    length: float
    position: float
    radius: float
