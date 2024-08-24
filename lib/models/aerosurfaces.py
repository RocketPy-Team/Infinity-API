from typing import Optional
from pydantic import BaseModel


class RailButtons(BaseModel):
    upper_button_position: float
    lower_button_position: float
    angular_position: float


class NoseCone(BaseModel):
    length: float
    kind: str
    position: float
    base_radius: float
    rocket_radius: float


class Fins(BaseModel):
    n: int
    root_chord: float
    tip_chord: float
    span: float
    position: float
    cant_angle: float
    radius: float
    airfoil: str


class TrapezoidalFins(Fins):
    pass


class Tail(BaseModel):
    top_radius: float
    bottom_radius: float
    length: float
    position: float
    radius: float
