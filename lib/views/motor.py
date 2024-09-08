from typing import List, Any, Optional
from pydantic import BaseModel
from lib.models.motor import Motor, MotorKinds


class MotorSummary(BaseModel):
    # TODO: if Any is Callable, jumps pydantic parsing, expects a dill binary object
    average_thrust: Optional[float]
    burn_duration: Optional[float]
    burn_out_time: Optional[float]
    burn_start_time: Optional[float]
    center_of_dry_mass_position: Optional[float]
    coordinate_system_orientation: Optional[str]
    dry_I_11: Optional[float]
    dry_I_12: Optional[float]
    dry_I_13: Optional[float]
    dry_I_22: Optional[float]
    dry_I_23: Optional[float]
    dry_I_33: Optional[float]
    dry_mass: Optional[float]
    grain_burn_out: Optional[float]
    grain_density: Optional[float]
    grain_initial_height: Optional[float]
    grain_initial_inner_radius: Optional[float]
    grain_initial_mass: Optional[float]
    grain_initial_volume: Optional[float]
    grain_number: Optional[int]
    grain_outer_radius: Optional[float]
    grain_separation: Optional[float]
    grains_center_of_mass_position: Optional[float]
    interpolate: Optional[str]
    max_thrust: Optional[float]
    max_thrust_time: Optional[float]
    nozzle_position: Optional[float]
    nozzle_radius: Optional[float]
    propellant_initial_mass: Optional[float]
    throat_area: Optional[float]
    throat_radius: Optional[float]
    thrust_source: Optional[List[List[float]]]
    total_impulse: Optional[float]
    Kn: Optional[Any]
    I_11: Optional[Any]
    I_12: Optional[Any]
    I_13: Optional[Any]
    I_22: Optional[Any]
    I_23: Optional[Any]
    I_33: Optional[Any]
    burn_area: Optional[Any]
    burn_rate: Optional[Any]
    burn_time: Optional[Any]
    center_of_mass: Optional[Any]
    center_of_propellant_mass: Optional[Any]
    exhaust_velocity: Optional[Any]
    grain_height: Optional[Any]
    grain_volume: Optional[Any]
    grain_inner_radius: Optional[Any]
    mass_flow_rate: Optional[Any]
    propellant_I_11: Optional[Any]
    propellant_I_12: Optional[Any]
    propellant_I_13: Optional[Any]
    propellant_I_22: Optional[Any]
    propellant_I_23: Optional[Any]
    propellant_I_33: Optional[Any]
    clip_thrust: Optional[Any]
    propellant_mass: Optional[Any]
    reshape_thrust_curve: Optional[Any]
    total_mass: Optional[Any]
    total_mass_flow_rate: Optional[Any]
    thrust: Optional[Any]


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
