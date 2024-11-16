from enum import Enum
from typing import Optional, Tuple, List, Union
from pydantic import BaseModel, PrivateAttr


class MotorKinds(str, Enum):
    HYBRID: str = "HYBRID"
    SOLID: str = "SOLID"
    GENERIC: str = "GENERIC"
    LIQUID: str = "LIQUID"


class TankKinds(str, Enum):
    LEVEL: str = "LEVEL"
    MASS: str = "MASS"
    MASS_FLOW: str = "MASSFLOW"
    ULLAGE: str = "ULLAGE"


class CoordinateSystemOrientation(str, Enum):
    NOZZLE_TO_COMBUSTION_CHAMBER: str = "NOZZLE_TO_COMBUSTION_CHAMBER"
    COMBUSTION_CHAMBER_TO_NOZZLE: str = "COMBUSTION_CHAMBER_TO_NOZZLE"


class TankFluids(BaseModel):
    name: str
    density: float


class InterpolationMethods(str, Enum):
    LINEAR: str = "LINEAR"
    SPLINE: str = "SPLINE"
    AKIMA: str = "AKIMA"
    POLYNOMIAL: str = "POLYNOMIAL"
    SHEPARD: str = "SHEPARD"
    RBF: str = "RBF"


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


class Motor(BaseModel):
    # Required parameters
    thrust_source: List[List[float]]
    burn_time: float
    nozzle_radius: float
    dry_mass: float
    dry_inertia: Tuple[float, float, float] = (0, 0, 0)
    center_of_dry_mass_position: float

    # Generic motor parameters
    chamber_radius: Optional[float] = None
    chamber_height: Optional[float] = None
    chamber_position: Optional[float] = None
    propellant_initial_mass: Optional[float] = None
    nozzle_position: Optional[float] = None

    # Liquid motor parameters
    tanks: Optional[List[MotorTank]] = None

    # Solid motor parameters
    grain_number: Optional[int] = None
    grain_density: Optional[float] = None
    grain_outer_radius: Optional[float] = None
    grain_initial_inner_radius: Optional[float] = None
    grain_initial_height: Optional[float] = None
    grains_center_of_mass_position: Optional[float] = None
    grain_separation: Optional[float] = None

    # Hybrid motor parameters
    throat_radius: Optional[float] = None

    # Optional parameters
    interpolation_method: InterpolationMethods = InterpolationMethods.LINEAR
    coordinate_system_orientation: CoordinateSystemOrientation = (
        CoordinateSystemOrientation.NOZZLE_TO_COMBUSTION_CHAMBER
    )
    reshape_thrust_curve: Union[bool, tuple] = False

    # Computed parameters
    _motor_kind: MotorKinds = PrivateAttr(default=MotorKinds.SOLID)

    @property
    def motor_kind(self) -> MotorKinds:
        return self._motor_kind

    def set_motor_kind(self, motor_kind: MotorKinds):
        self._motor_kind = motor_kind
