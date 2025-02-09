from typing import Optional, Tuple, List, Union, Self, ClassVar
from pydantic import PrivateAttr, model_validator

from lib.models.interface import ApiBaseModel
from lib.models.sub.tanks import MotorTank, TankFluids, TankKinds, InterpolationMethods, TankCoordinateSystemOrientation, MotorKinds, MotorTank


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
    coordinate_system_orientation: TankCoordinateSystemOrientation = (
        TankCoordinateSystemOrientation.NOZZLE_TO_COMBUSTION_CHAMBER
    )
    reshape_thrust_curve: Union[bool, tuple] = False

    # Computed parameters
    _motor_kind: MotorKinds = PrivateAttr(default=MotorKinds.SOLID)

    @model_validator(mode='after')
    # TODO: extend guard to check motor kinds and tank kinds specifics
    def validate_motor_kind(self):
        if (
            self._motor_kind not in (MotorKinds.SOLID, MotorKinds.GENERIC)
            and self.tanks is None
        ):
            raise ValueError("Tanks must be provided for liquid and hybrid motors.")
        return self

    @property
    def motor_kind(self) -> MotorKinds:
        return self._motor_kind

    def set_motor_kind(self, motor_kind: MotorKinds):
        self._motor_kind = motor_kind
        return self

    @staticmethod
    def UPDATED():
        from lib.views.motor import MotorUpdated

        return MotorUpdated()

    @staticmethod
    def DELETED():
        from lib.views.motor import MotorDeleted

        return MotorDeleted()

    @staticmethod
    def CREATED(model_id: str):
        from lib.views.motor import MotorCreated

        return MotorCreated(motor_id=model_id)

    @staticmethod
    def RETRIEVED(model_instance: type(Self)):
        from lib.views.motor import MotorRetrieved, MotorView

        return MotorRetrieved(
            motor=MotorView(
                motor_id=model_instance.get_id(),
                **model_instance.model_dump(),
            )
        )
