from enum import Enum
from typing import Optional
from pydantic import BaseModel
from lib.models.rocket import Rocket
from lib.models.environment import Env


class EquationsOfMotion(str, Enum):
    STANDARD = "STANDARD"
    SOLID_PROPULSION = "SOLID_PROPULSION"


class Flight(BaseModel):
    name: str = "Flight"
    environment: Env = Env()
    rocket: Rocket = Rocket()
    rail_length: float = 5.2
    inclination: Optional[int] = 80.0
    heading: Optional[int] = 90.0
    # TODO: implement initial_solution
    terminate_on_apogee: Optional[bool] = False
    max_time: Optional[int] = 600
    max_time_step: Optional[float] = 9999
    min_time_step: Optional[int] = 0
    rtol: Optional[float] = 1e-3
    atol: Optional[float] = 1e-3
    time_overshoot: Optional[bool] = True
    verbose: Optional[bool] = False
    equations_of_motion: Optional[EquationsOfMotion] = (
        EquationsOfMotion.STANDARD
    )
