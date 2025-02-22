from typing import Any, Optional
from pydantic import BaseModel, ConfigDict
from lib.models.rocket import Rocket, CoordinateSystemOrientation
from lib.views.motor import MotorView, MotorSummary
from lib.utils import to_python_primitive


class RocketSummary(MotorSummary):
    area: Optional[float] = None
    coordinate_system_orientation: str = (
        CoordinateSystemOrientation.TAIL_TO_NOSE.value
    )
    center_of_mass_without_motor: Optional[float] = None
    motor_center_of_dry_mass_position: Optional[float] = None
    motor_position: Optional[float] = None
    nozzle_position: Optional[float] = None
    nozzle_to_cdm: Optional[float] = None
    cp_eccentricity_x: Optional[float] = None
    cp_eccentricity_y: Optional[float] = None
    thrust_eccentricity_x: Optional[float] = None
    thrust_eccentricity_y: Optional[float] = None
    I_11_without_motor: Optional[Any] = None
    I_12_without_motor: Optional[Any] = None
    I_13_without_motor: Optional[Any] = None
    I_22_without_motor: Optional[Any] = None
    I_23_without_motor: Optional[Any] = None
    I_33_without_motor: Optional[Any] = None
    check_parachute_trigger: Optional[Any] = None
    com_to_cdm_function: Optional[Any] = None
    cp_position: Optional[Any] = None
    motor_center_of_mass_position: Optional[Any] = None
    nozzle_gyration_tensor: Optional[Any] = None
    power_off_drag: Optional[Any] = None
    power_on_drag: Optional[Any] = None
    reduced_mass: Optional[Any] = None
    stability_margin: Optional[Any] = None
    static_margin: Optional[Any] = None
    thrust_to_weight: Optional[Any] = None
    total_lift_coeff_der: Optional[Any] = None

    model_config = ConfigDict(json_encoders={Any: to_python_primitive})


class RocketCreated(BaseModel):
    rocket_id: str
    message: str = "Rocket successfully created"


class RocketUpdated(BaseModel):
    rocket_id: str
    message: str = "Rocket successfully updated"


class RocketDeleted(BaseModel):
    rocket_id: str
    message: str = "Rocket successfully deleted"


class RocketView(Rocket):
    motor: MotorView
