from pydantic import BaseModel
from typing import Optional

class RailButtons(BaseModel, frozen=True):
    upper_button_position: Optional[float] = -0.5
    lower_button_position: Optional[float] = 0.2
    angular_position: Optional[float] = 45 
    
class NoseCone(BaseModel, frozen=True):
    length: float
    kind: str
    position: float
    base_radius: float
    rocket_radius: float

class Fins(BaseModel, frozen=True):
    n: int
    root_chord: float
    tip_chord: float
    span: float
    position: float
    cant_angle: float
    radius: float
    airfoil: str

class TrapezoidalFins(Fins, frozen=True):
    def __init__():
        super().__init__()
    
class Tail(BaseModel, frozen=True):
    top_radius: float
    bottom_radius: float
    length: float
    position: float
    radius: float

