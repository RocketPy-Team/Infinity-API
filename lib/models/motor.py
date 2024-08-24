from enum import Enum
from typing import Optional, Tuple, List, Union
from rocketpy import (
    LevelBasedTank,
    MassBasedTank,
    MassFlowRateBasedTank,
    UllageBasedTank,
    TankGeometry,
)
from pydantic import BaseModel, PrivateAttr


class MotorKinds(str, Enum):
    HYBRID: str = "HYBRID"
    SOLID: str = "SOLID"
    LIQUID: str = "LIQUID"


class MotorEngines(str, Enum):
    CESARONI_M1670: str = "CESARONI_M1670"
    CUSTOM: str = "CUSTOM"


class TankKinds(str, Enum):
    LEVEL: str = "LEVEL"
    MASS: str = "MASS"
    MASS_FLOW: str = "MASSFlOW"
    ULLAGE: str = "ULLAGE"


class TankFluids(BaseModel):
    name: str
    density: float


class MotorTank(BaseModel):
    # Required parameters
    geometry: List[Tuple[Tuple[float, float], float]] = [
        ((0.0, 5.0), 1.0),
        ((5.0, 10.0), 2.0),
    ]
    tank_kind: TankKinds = TankKinds.MASS_FLOW
    gas: TankFluids = TankFluids(name="GAS", density=100)
    liquid: TankFluids = TankFluids(name="LIQUID", density=1000)
    name: str = "Tank"
    flux_time: Tuple[float, float] = (0.0, 3.9)
    position: float = 1.0
    discretize: int = 100

    # Optional parameters
    liquid_height: Optional[float] = 0.5
    liquid_mass: Optional[float] = 5.0
    gas_mass: Optional[float] = 0.1
    gas_mass_flow_rate_in: Optional[float] = 0.0
    gas_mass_flow_rate_out: Optional[float] = 0.1
    liquid_mass_flow_rate_in: Optional[float] = 0.0
    liquid_mass_flow_rate_out: Optional[float] = 1
    initial_liquid_mass: Optional[float] = 5.0
    initial_gas_mass: Optional[float] = 0.4
    ullage: Optional[float] = 0.1

    _tank: Union[
        LevelBasedTank, MassBasedTank, MassFlowRateBasedTank, UllageBasedTank
    ] = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        tank_core = {
            "name": self.name,
            "geometry": TankGeometry(geometry_dict=dict(self.geometry)),
            "flux_time": self.flux_time,
            "gas": self.gas,
            "liquid": self.liquid,
            "discretize": self.discretize,
        }

        match self.tank_kind:
            case TankKinds.LEVEL:
                tank = LevelBasedTank(
                    **tank_core, liquid_height=self.liquid_height
                )
            case TankKinds.MASS:
                tank = MassBasedTank(
                    **tank_core,
                    liquid_mass=self.liquid_mass,
                    gas_mass=self.gas_mass,
                )
            case TankKinds.MASS_FLOW:
                tank = MassFlowRateBasedTank(
                    **tank_core,
                    gas_mass_flow_rate_in=self.gas_mass_flow_rate_in,
                    gas_mass_flow_rate_out=self.gas_mass_flow_rate_out,
                    liquid_mass_flow_rate_in=self.liquid_mass_flow_rate_in,
                    liquid_mass_flow_rate_out=self.liquid_mass_flow_rate_out,
                    initial_liquid_mass=self.initial_liquid_mass,
                    initial_gas_mass=self.initial_gas_mass,
                )
            case TankKinds.ullage:
                tank = UllageBasedTank(**tank_core, ullage=self.ullage)
        self._tank = tank

    @property
    def tank(self):
        return self._tank


class Motor(BaseModel):
    # Required parameters
    thrust_source: MotorEngines = MotorEngines.CESARONI_M1670
    burn_time: float = 3.9
    nozzle_radius: float = 0.033
    dry_mass: float = 1.815
    dry_inertia: Tuple[float, float, float] = (0.125, 0.125, 0.002)
    center_of_dry_mass_position: float = 0.317
    _motor_kind: MotorKinds = PrivateAttr(default=MotorKinds.SOLID)

    # Optional parameters
    tanks: Optional[List[MotorTank]] = [MotorTank()]
    grain_number: Optional[int] = 5
    grain_density: Optional[float] = 1815
    grain_outer_radius: Optional[float] = 0.033
    grain_initial_inner_radius: Optional[float] = 0.015
    grain_initial_height: Optional[float] = 0.12
    grains_center_of_mass_position: Optional[float] = -0.85704
    grain_separation: Optional[float] = 0.005
    throat_radius: Optional[float] = 0.011
    interpolation_method: Optional[str] = "linear"
    coordinate_system_orientation: Optional[str] = (
        "nozzle_to_combustion_chamber"
    )

    @property
    def motor_kind(self) -> MotorKinds:
        return self._motor_kind

    def set_motor_kind(self, motor_kind: MotorKinds):
        self._motor_kind = motor_kind
