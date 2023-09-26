from typing import Optional, Tuple
from enum import Enum
from pydantic import BaseModel

class MotorOptions(str, Enum):
    cesaroni: str = "Cesaroni_M1670"
    custom: str = "Custom (Coming soon)"

class Motor(BaseModel, frozen=True):
    burn_time: float = 3.9
    dry_mass: float = 1.815
    dry_inertia: "Tuple[float, float, float]" = (0.125, 0.125, 0.002)
    center_of_dry_mass_position: float = 0.317
    grain_number: int = 5
    grain_density: float = 1815
    grain_outer_radius: float = 0.033
    grain_initial_inner_radius: float = 0.015
    grain_initial_height: float = 0.12
    grains_center_of_mass_position: float = -0.85704
    #TBD: thrust_source must be the id of a previously uploaded .eng file and a list of "default" files must be provided in the api docs
    thrust_source: MotorOptions = "Cesaroni_M1670"
    grain_separation: float = 0.005
    nozzle_radius: float = 0.033
    throat_radius: float = 0.011
    interpolation_method: str = "linear"
    coordinate_system_orientation: str = "nozzle_to_combustion_chamber"
