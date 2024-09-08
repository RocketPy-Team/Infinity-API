from typing import Any, Optional
from pydantic import BaseModel
from lib.models.rocket import Rocket
from lib.views.motor import MotorView, MotorSummary


class RocketSummary(MotorSummary):
    # TODO: if Any is Callable, jumps pydantic parsing, expects a dill binary object
    area: Optional[float]
    center_of_mass_without_motor: Optional[float]
    motor_center_of_dry_mass_position: Optional[float]
    motor_position: Optional[float]
    nozzle_position: Optional[float]
    nozzle_to_cdm: Optional[float]
    cp_eccentricity_x: Optional[float]
    cp_eccentricity_y: Optional[float]
    thrust_eccentricity_x: Optional[float]
    thrust_eccentricity_y: Optional[float]
    I_11_without_motor: Optional[Any]
    I_12_without_motor: Optional[Any]
    I_13_without_motor: Optional[Any]
    I_22_without_motor: Optional[Any]
    I_23_without_motor: Optional[Any]
    I_33_without_motor: Optional[Any]
    check_parachute_trigger: Optional[Any]
    com_to_cdm_function: Optional[Any]
    cp_position: Optional[Any]
    motor_center_of_mass_position: Optional[Any]
    nozzle_gyration_tensor: Optional[Any]
    power_off_drag: Optional[Any]
    power_on_drag: Optional[Any]
    reduced_mass: Optional[Any]
    stability_margin: Optional[Any]
    static_margin: Optional[Any]
    thrust_to_weight: Optional[Any]
    total_lift_coeff_der: Optional[Any]


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
