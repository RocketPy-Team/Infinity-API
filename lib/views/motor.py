from typing import List, Any, Optional
from pydantic import BaseModel
from lib.models.motor import Motor, MotorKinds, CoordinateSystemOrientation
from lib.utils import to_python_primitive


class MotorSummary(BaseModel):
    average_thrust: Optional[float] = None
    burn_duration: Optional[float] = None
    burn_out_time: Optional[float] = None
    burn_start_time: Optional[float] = None
    center_of_dry_mass_position: Optional[float] = None
    coordinate_system_orientation: str = (
        CoordinateSystemOrientation.NOZZLE_TO_COMBUSTION_CHAMBER.value
    )
    dry_I_11: Optional[float] = None
    dry_I_12: Optional[float] = None
    dry_I_13: Optional[float] = None
    dry_I_22: Optional[float] = None
    dry_I_23: Optional[float] = None
    dry_I_33: Optional[float] = None
    dry_mass: Optional[float] = None
    grain_burn_out: Optional[float] = None
    grain_density: Optional[float] = None
    grain_initial_height: Optional[float] = None
    grain_initial_inner_radius: Optional[float] = None
    grain_initial_mass: Optional[float] = None
    grain_initial_volume: Optional[float] = None
    grain_number: Optional[int] = None
    grain_outer_radius: Optional[float] = None
    grain_separation: Optional[float] = None
    grains_center_of_mass_position: Optional[float] = None
    interpolate: Optional[str] = None
    max_thrust: Optional[float] = None
    max_thrust_time: Optional[float] = None
    nozzle_position: Optional[float] = None
    nozzle_radius: Optional[float] = None
    propellant_initial_mass: Optional[float] = None
    throat_area: Optional[float] = None
    throat_radius: Optional[float] = None
    thrust_source: Optional[List[List[float]]] = None
    total_impulse: Optional[float] = None
    Kn: Optional[Any] = None
    I_11: Optional[Any] = None
    I_12: Optional[Any] = None
    I_13: Optional[Any] = None
    I_22: Optional[Any] = None
    I_23: Optional[Any] = None
    I_33: Optional[Any] = None
    burn_area: Optional[Any] = None
    burn_rate: Optional[Any] = None
    burn_time: Optional[Any] = None
    center_of_mass: Optional[Any] = None
    center_of_propellant_mass: Optional[Any] = None
    exhaust_velocity: Optional[Any] = None
    grain_height: Optional[Any] = None
    grain_volume: Optional[Any] = None
    grain_inner_radius: Optional[Any] = None
    mass_flow_rate: Optional[Any] = None
    propellant_I_11: Optional[Any] = None
    propellant_I_12: Optional[Any] = None
    propellant_I_13: Optional[Any] = None
    propellant_I_22: Optional[Any] = None
    propellant_I_23: Optional[Any] = None
    propellant_I_33: Optional[Any] = None
    propellant_mass: Optional[Any] = None
    reshape_thrust_curve: Optional[Any] = None
    total_mass: Optional[Any] = None
    total_mass_flow_rate: Optional[Any] = None
    thrust: Optional[Any] = None

    class Config:
        json_encoders = {Any: to_python_primitive}


class MotorCreated(BaseModel):
    motor_id: str
    message: str = "Motor successfully created"


class MotorUpdated(BaseModel):
    motor_id: str
    message: str = "Motor successfully updated"


class MotorDeleted(BaseModel):
    motor_id: str
    message: str = "Motor successfully deleted"


class MotorView(Motor):
    selected_motor_kind: MotorKinds
