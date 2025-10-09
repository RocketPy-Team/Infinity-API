from typing import Optional, Tuple, List, Union, Literal
from pydantic import BaseModel, Field


class Parachute(BaseModel):
    name: str
    cd_s: float = Field(..., ge=0, description="Must be non-negative")
    sampling_rate: float = Field(..., gt=0, description="Must be positive")
    lag: float = Field(..., ge=0, description="Must be non-negative")
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


class Fins(BaseModel):
    fins_kind: Literal['trapezoidal', 'elliptical']
    name: str
    n: int
    root_chord: float
    span: float
    position: float
    # Optional parameters
    tip_chord: Optional[float] = None
    cant_angle: Optional[float] = None
    rocket_radius: Optional[float] = None
    airfoil: Optional[
        Tuple[List[Tuple[float, float]], Literal['radians', 'degrees']]
    ] = None
    sweep_length: Optional[float] = None
    sweep_angle: Optional[float] = None

    _base_keys = {"fins_kind", "name", "n", "root_chord", "span", "position"}

    def get_additional_parameters(self):
        params = {
            k: v for k, v in self.dict().items()
            if v is not None and k not in self._base_keys
        }
        if "sweep_angle" in params and "sweep_length" in params:
            params.pop("sweep_length")

        return params


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
