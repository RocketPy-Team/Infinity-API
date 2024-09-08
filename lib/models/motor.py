from enum import Enum
from typing import Optional, Tuple, List
from pydantic import BaseModel, PrivateAttr


class MotorKinds(str, Enum):
    HYBRID: str = "HYBRID"
    SOLID: str = "SOLID"
    GENERIC: str = "GENERIC"
    LIQUID: str = "LIQUID"


class TankKinds(str, Enum):
    LEVEL: str = "LEVEL"
    MASS: str = "MASS"
    MASS_FLOW: str = "MASSFlOW"
    ULLAGE: str = "ULLAGE"


class CoordinateSystemOrientation(str, Enum):
    NOZZLE_TO_COMBUSTION_CHAMBER: str = "NOZZLE_TO_COMBUSTION_CHAMBER"
    COMBUSTION_CHAMBER_TO_NOZZLE: str = "COMBUSTION_CHAMBER_TO_NOZZLE"


class TankFluids(BaseModel):
    name: str
    density: float


class MotorTank(BaseModel):
    # Required parameters
    geometry: List[Tuple[Tuple[float, float], float]] = [
        ((0.0, 5.0), 1.0),
        ((5.0, 10.0), 2.0),
    ]
    gas: TankFluids = TankFluids(name="GAS", density=100)
    liquid: TankFluids = TankFluids(name="LIQUID", density=1000)
    flux_time: Tuple[float, float] = (0.0, 3.9)
    position: float = 1.0
    discretize: int = 100

    # Level based tank parameters
    liquid_height: Optional[float] = 0.5

    # Mass based tank parameters
    liquid_mass: Optional[float] = 5.0
    gas_mass: Optional[float] = 0.1

    # Mass flow based tank parameters
    gas_mass_flow_rate_in: Optional[float] = 0.0
    gas_mass_flow_rate_out: Optional[float] = 0.1
    liquid_mass_flow_rate_in: Optional[float] = 0.0
    liquid_mass_flow_rate_out: Optional[float] = 1
    initial_liquid_mass: Optional[float] = 5.0
    initial_gas_mass: Optional[float] = 0.4

    # Ullage based tank parameters
    ullage: Optional[float] = 0.1

    # Optional parameters
    name: Optional[str] = "Tank"

    # Computed parameters
    tank_kind: TankKinds = TankKinds.MASS_FLOW


class Motor(BaseModel):
    # Required parameters
    thrust_source: List[List[float]] = [[0.0, 0.0], [1.0, 1.0]]
    burn_time: float = 3.9
    nozzle_radius: float = 0.033
    dry_mass: float = 1.815
    dry_inertia: Tuple[float, float, float] = (0.125, 0.125, 0.002)
    center_of_dry_mass_position: float = 0.317

    # Generic motor parameters
    chamber_radius: Optional[float] = 0.033
    chamber_height: Optional[float] = 0.1
    chamber_position: Optional[float] = 0.0
    propellant_initial_mass: Optional[float] = 1.0
    nozzle_position: Optional[float] = 0.0

    # Liquid motor parameters
    tanks: Optional[List[MotorTank]] = [MotorTank()]

    # Solid motor parameters
    grain_number: Optional[int] = 5
    grain_density: Optional[float] = 1815
    grain_outer_radius: Optional[float] = 0.033
    grain_initial_inner_radius: Optional[float] = 0.015
    grain_initial_height: Optional[float] = 0.12
    grains_center_of_mass_position: Optional[float] = -0.85704
    grain_separation: Optional[float] = 0.005

    # Hybrid motor parameters
    throat_radius: Optional[float] = 0.011

    # Optional parameters
    interpolation_method: Optional[str] = "linear"
    coordinate_system_orientation: Optional[CoordinateSystemOrientation] = (
        CoordinateSystemOrientation.NOZZLE_TO_COMBUSTION_CHAMBER
    )
    reshape_thrust_curve: Optional[bool] = False

    # Computed parameters
    _motor_kind: MotorKinds = PrivateAttr(default=MotorKinds.SOLID)

    @property
    def motor_kind(self) -> MotorKinds:
        return self._motor_kind

    def set_motor_kind(self, motor_kind: MotorKinds):
        self._motor_kind = motor_kind
