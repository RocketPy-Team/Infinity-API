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
    rail_length: float = 1
    time_overshoot: bool = True
    terminate_on_apogee: bool = True
    equations_of_motion: EquationsOfMotion = EquationsOfMotion.STANDARD

    # Optional parameters
    inclination: Optional[int] = None
    heading: Optional[int] = None
    # TODO: implement initial_solution
    max_time: Optional[int] = None
    max_time_step: Optional[float] = None
    min_time_step: Optional[int] = None
    rtol: Optional[float] = None
    atol: Optional[float] = None
    verbose: Optional[bool] = None

    def get_additional_parameters(self):
        return {
            key: value
            for key, value in self.dict().items()
            if value is not None
            and key
            not in [
                "name",
                "environment",
                "rocket",
                "rail_length",
                "time_overshoot",
                "terminate_on_apogee",
                "equations_of_motion",
            ]
        }
