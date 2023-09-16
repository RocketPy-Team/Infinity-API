from pydantic import BaseModel
from typing import Optional, Tuple

class Motor(BaseModel, frozen=True):
    burn_time: float
    dry_mass: float
    dry_inertia: "Tuple[float, float, float]"
    center_of_dry_mass_position: float
    grain_number: int
    grain_density: float
    grain_outer_radius: float
    grain_initial_inner_radius: float
    grain_initial_height: float
    grains_center_of_mass_position: float
    #TBD: thrust_source must be the id of a previously uploaded .eng file and a list of "default" files must be provided in the api docs
    thrust_source: Optional[str] = "lib/data/motors/Cesaroni_M1670.eng"
    grain_separation: float
    nozzle_radius: float
    throat_radius: float
    interpolation_method: str
    coordinate_system_orientation: str
