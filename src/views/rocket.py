from typing import Optional
from src.models.rocket import RocketModel
from src.views.interface import ApiBaseView
from src.views.motor import MotorView, MotorSimulation
from src.utils import AnyToPrimitive


class RocketSimulation(MotorSimulation):
    message: str = "Rocket successfully simulated"
    area: Optional[float] = None
    coordinate_system_orientation: str = 'tail_to_nose'
    center_of_mass_without_motor: Optional[float] = None
    motor_center_of_dry_mass_position: Optional[float] = None
    motor_position: Optional[float] = None
    nozzle_position: Optional[float] = None
    nozzle_to_cdm: Optional[float] = None
    cp_eccentricity_x: Optional[float] = None
    cp_eccentricity_y: Optional[float] = None
    thrust_eccentricity_x: Optional[float] = None
    thrust_eccentricity_y: Optional[float] = None
    I_11_without_motor: Optional[AnyToPrimitive] = None
    I_12_without_motor: Optional[AnyToPrimitive] = None
    I_13_without_motor: Optional[AnyToPrimitive] = None
    I_22_without_motor: Optional[AnyToPrimitive] = None
    I_23_without_motor: Optional[AnyToPrimitive] = None
    I_33_without_motor: Optional[AnyToPrimitive] = None
    check_parachute_trigger: Optional[AnyToPrimitive] = None
    com_to_cdm_function: Optional[AnyToPrimitive] = None
    cp_position: Optional[AnyToPrimitive] = None
    motor_center_of_mass_position: Optional[AnyToPrimitive] = None
    nozzle_gyration_tensor: Optional[AnyToPrimitive] = None
    power_off_drag: Optional[AnyToPrimitive] = None
    power_on_drag: Optional[AnyToPrimitive] = None
    reduced_mass: Optional[AnyToPrimitive] = None
    stability_margin: Optional[AnyToPrimitive] = None
    static_margin: Optional[AnyToPrimitive] = None
    thrust_to_weight: Optional[AnyToPrimitive] = None
    total_lift_coeff_der: Optional[AnyToPrimitive] = None


class RocketView(RocketModel):
    rocket_id: Optional[str] = None
    motor: MotorView


class RocketCreated(ApiBaseView):
    message: str = "Rocket successfully created"
    rocket_id: str


class RocketRetrieved(ApiBaseView):
    message: str = "Rocket successfully retrieved"
    rocket: RocketView
