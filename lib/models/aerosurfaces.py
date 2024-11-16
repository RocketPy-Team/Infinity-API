from enum import Enum
from typing import Optional, Tuple, List, Union
from pydantic import BaseModel


class Parachute(BaseModel):
    name: str
    cd_s: float
    sampling_rate: int
    lag: float
    trigger: Union[str, float]
    noise: Tuple[float, float, float]


class RailButtons(BaseModel):
    name: str = "RailButtons"
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


class AngleUnit(str, Enum):
    RADIANS: str = "RADIANS"
    DEGREES: str = "DEGREES"


class Fins(BaseModel):
    fins_kind: FinsKinds
    name: str
    n: int
    root_chord: float
    span: float
    position: float

    # Optional parameters
    tip_chord: Optional[float] = None
    cant_angle: Optional[float] = None
    rocket_radius: Optional[float] = None
    airfoil: Optional[Tuple[List[Tuple[float, float]], AngleUnit]] = None

    def get_additional_parameters(self):
        return {
            key: value
            for key, value in self.dict().items()
            if value is not None
            and key
            not in ["fins_kind", "name", "n", "root_chord", "span", "position"]
        }


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
