from enum import Enum
from typing import Annotated, List, Literal, Optional, Tuple, Union

from pydantic import BaseModel, Field, model_validator


class TankKinds(str, Enum):
    LEVEL: str = "LEVEL"
    MASS: str = "MASS"
    MASS_FLOW: str = "MASS_FLOW"
    ULLAGE: str = "ULLAGE"


# Scalar density keeps the legacy behaviour (constant kg/m^3).
# A list of (temperature_K, density_kg_per_m3) samples enables
# temperature-dependent density — required for realistic LOX / N2O
# modelling. Pressure dependence is out of scope for this iteration.
DensityInput = Union[float, List[Tuple[float, float]]]


class TankFluids(BaseModel):
    name: str
    density: DensityInput


# --- Tank geometry discriminated union ----------------------------------
# RocketPy ships three concrete geometry classes. We mirror them as a
# discriminated Pydantic union keyed on `geometry_kind`. `custom` is the
# generic piecewise form (original API shape); `cylindrical` and
# `spherical` map to `rocketpy.motors.CylindricalTank` and
# `SphericalTank` respectively.


class CustomTankGeometry(BaseModel):
    geometry_kind: Literal["custom"] = "custom"
    geometry: List[Tuple[Tuple[float, float], float]]


class CylindricalTankGeometry(BaseModel):
    geometry_kind: Literal["cylindrical"] = "cylindrical"
    radius: float
    height: float
    spherical_caps: bool = False


class SphericalTankGeometry(BaseModel):
    geometry_kind: Literal["spherical"] = "spherical"
    radius: float


TankGeometryInput = Annotated[
    Union[
        CustomTankGeometry,
        CylindricalTankGeometry,
        SphericalTankGeometry,
    ],
    Field(discriminator="geometry_kind"),
]


# Map tank_kind → tuple of MotorTank field names that rocketpy's
# corresponding Tank subclass requires. The validator below rejects
# payloads that omit any of them so the API returns 422 instead of
# letting rocketpy crash during motor construction.
_REQUIRED_FIELDS_BY_TANK_KIND = {
    TankKinds.MASS_FLOW: (
        "initial_liquid_mass",
        "initial_gas_mass",
        "liquid_mass_flow_rate_in",
        "liquid_mass_flow_rate_out",
        "gas_mass_flow_rate_in",
        "gas_mass_flow_rate_out",
    ),
    TankKinds.LEVEL: ("liquid_height",),
    TankKinds.ULLAGE: ("ullage",),
    TankKinds.MASS: ("liquid_mass", "gas_mass"),
}


class MotorTank(BaseModel):
    # Required parameters
    geometry: TankGeometryInput
    gas: TankFluids
    liquid: TankFluids
    flux_time: Tuple[float, float]
    position: float
    # discretize is optional in RocketPy's Tank classes (defaults to 100).
    discretize: int = 100

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

    @model_validator(mode='after')
    def validate_tank_kind_fields(self):
        # Mirrors the validate_dry_inertia_for_kind pattern used on
        # MotorModel: reject incoherent payloads at the API boundary
        # instead of letting rocketpy crash during Tank construction.
        missing = [
            field
            for field in _REQUIRED_FIELDS_BY_TANK_KIND[self.tank_kind]
            if getattr(self, field) is None
        ]
        if missing:
            raise ValueError(
                f"tank_kind={self.tank_kind.value} requires: "
                f"{', '.join(missing)}"
            )
        return self
