from pydantic import BaseModel
from typing import Optional

class Motor(BaseModel, frozen=True):
    burnOut: float
    grainNumber: int
    grainDensity: float
    grainOuterRadius: float
    grainInitialInnerRadius: float
    grainInitialHeight: float
    grainsCenterOfMassPosition: float
    #TBD: thrustSource must be the id of a previously uploaded .eng file and a list of "default" files must be provided in the api docs
    thrustSource: Optional[str] = "lib/data/motors/Cesaroni_M1670.eng"
    grainSeparation: float
    nozzleRadius: float
    throatRadius: float
    interpolationMethod: str
