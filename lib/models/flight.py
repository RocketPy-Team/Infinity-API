from enum import Enum
from typing import Optional
from pydantic import BaseModel
from lib.models.rocket import Rocket
from lib.models.environment import Env


class EquationsOfMotion(str, Enum):
    STANDARD: str = "STANDARD"
    SOLID_PROPULSION: str = "SOLID_PROPULSION"


class Flight(BaseModel):
    name: str = "Flight"
    environment: Env
    rocket: Rocket
    rail_length: float
    inclination: Optional[int] = None
    heading: Optional[int] = None
    # TODO: implement initial_solution
    terminate_on_apogee: Optional[bool] = None
    max_time: Optional[int] = None
    max_time_step: Optional[float] = None
    min_time_step: Optional[int] = None
    rtol: Optional[float] = None
    atol: Optional[float] = None
    time_overshoot: Optional[bool] = None
    verbose: Optional[bool] = None
    equations_of_motion: Optional[EquationsOfMotion] = None
