from enum import Enum
from typing import Optional, Tuple, List
from rocketpy import (
    LevelBasedTank,
    MassBasedTank,
    MassFlowRateBasedTank,
    UllageBasedTank,
    TankGeometry,
)
from pydantic import BaseModel, PrivateAttr


class MotorKinds(str, Enum):
    hybrid: str = "Hybrid"
    solid: str = "Solid"
    liquid: str = "Liquid"


class MotorEngines(str, Enum):
    cesaroni: str = "Cesaroni_M1670"
    custom: str = "Custom"


class TankKinds(str, Enum):
    level: str = "Level"
    mass: str = "Mass"
    mass_flow: str = "MassFlow"
    ullage: str = "Ullage"


class TankFluids(BaseModel, frozen=True):
    name: str = "FluidName"
    density: float = 100.0


class MotorTank(BaseModel, frozen=True):
    # Required parameters
    geometry: "List[Tuple[Tuple[float,float],float]]" = [
        ((0, 5), 1),
        ((5, 10), 2),
    ]
    tank_kind: TankKinds = TankKinds.mass_flow
    gas: TankFluids = TankFluids()
    liquid: TankFluids = TankFluids()
    name: str = "Tank"
    flux_time: "List[float]" = [0, 8]
    position: float = 1.0

    # Optional parameters
    discretize: Optional[int] = 100
    liquid_height: Optional[float] = 0.5
    liquid_mass: Optional[float] = 5.0
    gas_mass: Optional[float] = 0.1
    gas_mass_flow_rate_in: Optional[float] = 0.1
    gas_mass_flow_rate_out: Optional[float] = 0.1
    liquid_mass_flow_rate_in: Optional[float] = 0.1
    liquid_mass_flow_rate_out: Optional[float] = 0.1
    initial_liquid_mass: Optional[float] = 5.0
    initial_gas_mass: Optional[float] = 0.1
    ullage: Optional[float] = 0.1

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
            case TankKinds.level:
                tank = LevelBasedTank(
                    **tank_core, liquid_height=self.liquid_height
                )
            case TankKinds.mass:
                tank = MassBasedTank(
                    **tank_core,
                    liquid_mass=self.liquid_mass,
                    gas_mass=self.gas_mass,
                )
            case TankKinds.mass_flow:
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
        object.__setattr__(self, "tank", tank)

    def __hash__(self):
        temp = vars(self)
        temp = str(temp)
        return hash(temp)


class Motor(BaseModel, frozen=True):
    # TODO: thrust_source must be the id of a previously uploaded .eng file and a list of "default" files must be provided in the api docs

    # Required parameters
    thrust_source: MotorEngines = MotorEngines.cesaroni
    burn_time: float = 3.9
    nozzle_radius: float = 0.033
    dry_mass: float = 1.815
    dry_inertia: "Tuple[float, float, float]" = (0.125, 0.125, 0.002)
    center_of_dry_mass_position: float = 0.317
    _motor_kind: MotorKinds = PrivateAttr()

    # Optional parameters
    tanks: Optional["List[MotorTank]"] = [MotorTank()]
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

    def __init__(self, motor_kind=MotorKinds.solid, **kwargs):
        super().__init__(**kwargs)
        self._motor_kind = motor_kind

    @property
    def motor_kind(self) -> MotorKinds:
        return self._motor_kind

    def __hash__(self):
        temp = vars(self)
        temp = str(temp)
        return hash(temp)
