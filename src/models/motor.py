import json
from enum import Enum
from typing import Optional, Tuple, List, Union, Self, ClassVar, Literal
from pydantic import model_validator, field_validator

from src.models.interface import ApiBaseModel
from src.models.sub.tanks import MotorTank


class MotorKinds(str, Enum):
    HYBRID: str = "HYBRID"
    SOLID: str = "SOLID"
    GENERIC: str = "GENERIC"
    LIQUID: str = "LIQUID"


class MotorModel(ApiBaseModel):
    NAME: ClassVar = 'motor'
    METHODS: ClassVar = ('POST', 'GET', 'PUT', 'DELETE')

    # Required parameters
    thrust_source: List[List[float]]
    burn_time: float
    nozzle_radius: float
    dry_mass: float
    dry_inertia: Tuple[float, float, float] = (0, 0, 0)
    center_of_dry_mass_position: float
    motor_kind: MotorKinds

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
    interpolation_method: Literal[
        'linear', 'spline', 'akima', 'polynomial', 'shepard', 'rbf'
    ] = 'linear'
    coordinate_system_orientation: Literal[
        'nozzle_to_combustion_chamber', 'combustion_chamber_to_nozzle'
    ] = 'nozzle_to_combustion_chamber'
    reshape_thrust_curve: Union[bool, tuple] = False

    @field_validator('tanks', mode='before')
    @classmethod
    def _coerce_tanks(cls, value):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as exc:
                raise ValueError('Invalid JSON for tanks payload') from exc
        if isinstance(value, dict):
            value = [value]
        return value

    @model_validator(mode='after')
    # TODO: extend guard to check motor kinds and tank kinds specifics
    def validate_motor_kind(self):
        if (
            self.motor_kind not in (MotorKinds.SOLID, MotorKinds.GENERIC)
            and self.tanks is None
        ):
            raise ValueError(
                "Tanks must be provided for liquid and hybrid motors."
            )
        return self

    @staticmethod
    def UPDATED():
        return

    @staticmethod
    def DELETED():
        return

    @staticmethod
    def CREATED(model_id: str):
        from src.views.motor import MotorCreated

        return MotorCreated(motor_id=model_id)

    @staticmethod
    def RETRIEVED(model_instance: type(Self)):
        from src.views.motor import MotorRetrieved, MotorView

        return MotorRetrieved(
            motor=MotorView(
                motor_id=model_instance.get_id(),
                **model_instance.model_dump(),
            )
        )
