from typing import Optional, Any
from pydantic import BaseModel

class InitialConditions(BaseModel):
    initial_position: str
    initial_velocity: str
    initial_altitude: str
    initial_angular_position: str
    initial_angular_velocity: str

class NumericalIntegrationSettings(BaseModel):
    max_time: str
    max_time_step: str
    min_time_step: str
    relative_error_tolerance: str
    absolute_error_tolerance: str
    time_overshoot: str
    terminate_on_apogee: str
    number_of_time_steps: str
    function_evaluations_per_time_step: str
    avg_function_evaluations_per_time_step: str

class SurfaceWindConditions(BaseModel):
    frontal_surface_wind_speed: str
    lateral_surface_wind_speed: str

class LaunchRailConditions(BaseModel):
    rail_length: str
    flight_inclination: str
    flight_heading: str

class OutOfRailConditions(BaseModel):
    out_of_rail_time: str
    out_of_rail_velocity: str
    out_of_rail_static_margin: str
    out_of_rail_angle_of_attack: str
    out_of_rail_thrust_weight_ratio: str
    out_of_rail_reynolds_number: str

class BurnoutConditions(BaseModel):
    burnout_time: str
    burnout_rocket_velocity: str
    burnout_altitude: str
    burnout_freestream_velocity: str
    burnout_mach_number: str
    burnout_kinetic_energy: str

class ApogeeConditions(BaseModel):
    apogee_time: str
    apogee_altitude: str
    apogee_freestream_speed: str

class MaximumValues(BaseModel):
    maximum_speed: str
    maximum_mach_number: str
    maximum_reynolds_number: str
    maximum_dynamic_pressure: str
    maximum_acceleration_during_motor_burn: str
    maximum_acceleration_after_motor_burn: str
    maximum_gs_during_motor_burn: str
    maximum_gs_after_motor_burn: str
    maximum_upper_rail_button_normal_force: str
    maximum_upper_rail_button_shear_force: str
    maximum_lower_rail_button_normal_force: str
    maximum_lower_rail_button_shear_force: str

class ImpactConditions(BaseModel):
    x_impact_position: "Optional[str]"
    y_impact_position: "Optional[str]"
    time_of_impact: "Optional[str]"
    impact_velocity: "Optional[str]"

class EventsRegistered(BaseModel):
    events_trace: "Optional[Any]"

class FlightData(BaseModel):
    initial_conditions: InitialConditions
    numerical_integration_settings: NumericalIntegrationSettings
    launch_rail_conditions: LaunchRailConditions
    surface_wind_conditions: SurfaceWindConditions
    out_of_rail_conditions: OutOfRailConditions
    burnout_conditions: BurnoutConditions
    apogee_conditions: ApogeeConditions
    maximum_values: MaximumValues
    impact_conditions: ImpactConditions
    events_registered: "Optional[EventsRegistered]"

class FlightPlots(BaseModel):
    pass

class FlightSummary(BaseModel):
    flight_data: FlightData
    #flight_plots: FlightPlots

class FlightCreated(BaseModel):
    flight_id: str 
    message: str = "Flight successfully created"

class FlightUpdated(BaseModel):
    new_flight_id: str 
    message: str = "Flight successfully updated"

class FlightDeleted(BaseModel):
    deleted_flight_id: str 
    message: str = "Flight successfully deleted"

class FlightPickle(BaseModel):
    jsonpickle_rocketpy_flight: str
