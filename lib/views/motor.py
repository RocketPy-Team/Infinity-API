from typing import List, Optional
from pydantic import BaseModel
from lib.views.interface import ApiBaseView
from lib.models.motor import MotorModel
from lib.utils import AnyToPrimitive


class MotorSimulation(BaseModel):
    average_thrust: Optional[float] = None
    burn_duration: Optional[float] = None
    burn_out_time: Optional[float] = None
    burn_start_time: Optional[float] = None
    center_of_dry_mass_position: Optional[float] = None
    coordinate_system_orientation: str = 'nozzle_to_combustion_chamber'
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
    Kn: Optional[AnyToPrimitive] = None
    I_11: Optional[AnyToPrimitive] = None
    I_12: Optional[AnyToPrimitive] = None
    I_13: Optional[AnyToPrimitive] = None
    I_22: Optional[AnyToPrimitive] = None
    I_23: Optional[AnyToPrimitive] = None
    I_33: Optional[AnyToPrimitive] = None
    burn_area: Optional[AnyToPrimitive] = None
    burn_rate: Optional[AnyToPrimitive] = None
    burn_time: Optional[AnyToPrimitive] = None
    center_of_mass: Optional[AnyToPrimitive] = None
    center_of_propellant_mass: Optional[AnyToPrimitive] = None
    exhaust_velocity: Optional[AnyToPrimitive] = None
    grain_height: Optional[AnyToPrimitive] = None
    grain_volume: Optional[AnyToPrimitive] = None
    grain_inner_radius: Optional[AnyToPrimitive] = None
    mass_flow_rate: Optional[AnyToPrimitive] = None
    propellant_I_11: Optional[AnyToPrimitive] = None
    propellant_I_12: Optional[AnyToPrimitive] = None
    propellant_I_13: Optional[AnyToPrimitive] = None
    propellant_I_22: Optional[AnyToPrimitive] = None
    propellant_I_23: Optional[AnyToPrimitive] = None
    propellant_I_33: Optional[AnyToPrimitive] = None
    propellant_mass: Optional[AnyToPrimitive] = None
    reshape_thrust_curve: Optional[AnyToPrimitive] = None
    total_mass: Optional[AnyToPrimitive] = None
    total_mass_flow_rate: Optional[AnyToPrimitive] = None
    thrust: Optional[AnyToPrimitive] = None


class MotorView(MotorModel):
    motor_id: Optional[str] = None


class MotorCreated(ApiBaseView):
    message: str = "Motor successfully created"
    motor_id: str


class MotorRetrieved(ApiBaseView):
    message: str = "Motor successfully retrieved"
    motor: MotorView


class MotorUpdated(ApiBaseView):
    message: str = "Motor successfully updated"


class MotorDeleted(ApiBaseView):
    message: str = "Motor successfully deleted"
