from typing import Optional
from pydantic import BaseModel


class RailButtons(BaseModel, frozen=True):
    upper_button_position: Optional[float] = -0.5
    lower_button_position: Optional[float] = 0.2
    angular_position: Optional[float] = 45


class NoseCone(BaseModel, frozen=True):
    length: float = 0.55829
    kind: str = "vonKarman"
    position: float = 1.278
    base_radius: float = 0.0635
    rocket_radius: float = 0.0635


class Fins(BaseModel, frozen=True):
    n: int = 4
    root_chord: float = 0.12
    tip_chord: float = 0.04
    span: float = 0.1
    position: float = -1.04956
    cant_angle: float = 0
    radius: float = 0.0635
    airfoil: str = ""


class TrapezoidalFins(Fins, frozen=True):
    pass


class Tail(BaseModel, frozen=True):
    top_radius: float = 0.0635
    bottom_radius: float = 0.0435
    length: float = 0.06
    position: float = -1.194656
    radius: float = 0.0635
