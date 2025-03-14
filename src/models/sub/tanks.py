from enum import Enum
from typing import Optional, Tuple, List
from pydantic import BaseModel


class TankKinds(str, Enum):
    LEVEL: str = "LEVEL"
    MASS: str = "MASS"
    MASS_FLOW: str = "MASS_FLOW"
    ULLAGE: str = "ULLAGE"


class TankFluids(BaseModel):
    name: str
    density: float


class MotorTank(BaseModel):
    # Required parameters
    geometry: List[Tuple[Tuple[float, float], float]]
    gas: TankFluids
    liquid: TankFluids
    flux_time: Tuple[float, float]
    position: float
    discretize: int

    # Level based tank parameters
    liquid_height: Optional[float] = None

    # Mass based tank parameters
    liquid_mass: Optional[float] = None
    gas_mass: Optional[float] = None

    # Mass flow based tank parameters
    gas_mass_flow_rate_in: Optional[float] = None
    gas_mass_flow_rate_out: Optional[float] = None
    liquid_mass_flow_rate_in: Optional[float] = None
    liquid_mass_flow_rate_out: Optional[float] = None
    initial_liquid_mass: Optional[float] = None
    initial_gas_mass: Optional[float] = None

    # Ullage based tank parameters
    ullage: Optional[float] = None

    # Optional parameters
    name: Optional[str] = None

    # Computed parameters
    tank_kind: TankKinds = TankKinds.MASS_FLOW
