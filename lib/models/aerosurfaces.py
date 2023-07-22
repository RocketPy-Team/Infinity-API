from pydantic import BaseModel
from typing import Optional

class RailButtons(BaseModel, frozen=True):
    upper_button_position: Optional[float] = -0.5
    lower_button_position: Optional[float] = 0.2
    angularPosition: Optional[float] = 45 
    
class NoseCone(BaseModel, frozen=True):
    length: float
    kind: str
    position: float
    baseRadius: float
    rocketRadius: float

class Fins(BaseModel, frozen=True):
    n: int
    rootChord: float
    tipChord: float
    span: float
    position: float
    cantAngle: float
    radius: float
    airfoil: str

class TrapezoidalFins(Fins, frozen=True):
    def __init__():
        super().__init__()
    
class Tail(BaseModel, frozen=True):
    topRadius: float
    bottomRadius: float
    length: float
    position: float
    radius: float

