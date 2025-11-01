from typing import Optional, Tuple, List, Union, Self, ClassVar, Literal

from pydantic import BaseModel, Field
from src.models.interface import ApiBaseModel
from src.models.motor import MotorModel
from src.models.sub.aerosurfaces import (
    Fins,
    NoseCone,
    Tail,
    RailButtons,
    Parachute,
)


class RocketModel(ApiBaseModel):
    NAME: ClassVar = "rocket"
    METHODS: ClassVar = ("POST", "GET", "PUT", "DELETE")

    # Required parameters
    motor: MotorModel
    radius: float
    mass: float
    motor_position: float
    center_of_mass_without_motor: float
    inertia: Union[
        Tuple[float, float, float],
        Tuple[float, float, float, float, float, float],
    ] = (0, 0, 0)
    power_off_drag: List[Tuple[float, float]] = [(0, 0)]
    power_on_drag: List[Tuple[float, float]] = [(0, 0)]
    coordinate_system_orientation: Literal['tail_to_nose', 'nose_to_tail'] = (
        'tail_to_nose'
    )
    nose: NoseCone
    fins: List[Fins]

    # Optional parameters
    parachutes: Optional[List[Parachute]] = None
    rail_buttons: Optional[RailButtons] = None
    tail: Optional[Tail] = None

    @staticmethod
    def UPDATED():
        return

    @staticmethod
    def DELETED():
        return

    @staticmethod
    def CREATED(model_id: str):
        from src.views.rocket import RocketCreated

        return RocketCreated(rocket_id=model_id)

    @staticmethod
    def RETRIEVED(model_instance: type(Self)):
        from src.views.rocket import RocketRetrieved, RocketView

        return RocketRetrieved(
            rocket=RocketView(
                rocket_id=model_instance.get_id(),
                **model_instance.model_dump(),
            )
        )


class RocketPartialModel(BaseModel):
    """Rocket attributes required when a motor is supplied by reference."""

    radius: float
    mass: float
    motor_position: float
    center_of_mass_without_motor: float
    inertia: Union[
        Tuple[float, float, float],
        Tuple[float, float, float, float, float, float],
    ] = (0, 0, 0)
    power_off_drag: List[Tuple[float, float]] = Field(
        default_factory=lambda: [(0, 0)]
    )
    power_on_drag: List[Tuple[float, float]] = Field(
        default_factory=lambda: [(0, 0)]
    )
    coordinate_system_orientation: Literal['tail_to_nose', 'nose_to_tail'] = (
        'tail_to_nose'
    )
    nose: NoseCone
    fins: List[Fins]
    parachutes: Optional[List[Parachute]] = None
    rail_buttons: Optional[RailButtons] = None
    tail: Optional[Tail] = None

    def assemble(self, motor: MotorModel) -> RocketModel:
        """Compose a full rocket model using the referenced motor."""

        rocket_data = self.model_dump(exclude_none=True)
        return RocketModel(motor=motor, **rocket_data)


class RocketWithMotorReferenceRequest(BaseModel):
    """Payload for creating or updating rockets via motor reference."""

    motor_id: str
    rocket: RocketPartialModel
