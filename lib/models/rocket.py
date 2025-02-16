from typing import Optional, Tuple, List, Union, Self, ClassVar, Literal
from lib.models.interface import ApiBaseModel
from lib.models.motor import MotorModel
from lib.models.sub.aerosurfaces import (
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
    center_of_mass_without_motor: int
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
        from lib.views.rocket import RocketUpdated

        return RocketUpdated()

    @staticmethod
    def DELETED():
        from lib.views.rocket import RocketDeleted

        return RocketDeleted()

    @staticmethod
    def CREATED(model_id: str):
        from lib.views.rocket import RocketCreated

        return RocketCreated(rocket_id=model_id)

    @staticmethod
    def RETRIEVED(model_instance: type(Self)):
        from lib.views.rocket import RocketRetrieved, RocketView

        return RocketRetrieved(
            rocket=RocketView(
                rocket_id=model_instance.get_id(),
                **model_instance.model_dump(),
            )
        )
