from typing import Optional, Any
from pydantic import BaseModel, ConfigDict
from lib.models.flight import Flight
from lib.views.rocket import RocketView, RocketSummary
from lib.views.environment import EnvSummary
from lib.utils import to_python_primitive


class FlightSummary(RocketSummary, EnvSummary):
    name: Optional[str] = None
    max_time: Optional[int] = None
    min_time_step: Optional[int] = None
    max_time_step: Optional[Any] = None
    equations_of_motion: Optional[str] = None
    heading: Optional[int] = None
    inclination: Optional[int] = None
    initial_solution: Optional[list] = None
    effective_1rl: Optional[float] = None
    effective_2rl: Optional[float] = None
    out_of_rail_time: Optional[float] = None
    out_of_rail_time_index: Optional[int] = None
    parachute_cd_s: Optional[float] = None
    rail_length: Optional[float] = None
    rtol: Optional[float] = None
    t: Optional[float] = None
    t_final: Optional[float] = None
    t_initial: Optional[int] = None
    terminate_on_apogee: Optional[bool] = None
    time_overshoot: Optional[bool] = None
    latitude: Optional[Any] = None
    longitude: Optional[Any] = None
    M1: Optional[Any] = None
    M2: Optional[Any] = None
    M3: Optional[Any] = None
    R1: Optional[Any] = None
    R2: Optional[Any] = None
    R3: Optional[Any] = None
    acceleration: Optional[Any] = None
    aerodynamic_bending_moment: Optional[Any] = None
    aerodynamic_drag: Optional[Any] = None
    aerodynamic_lift: Optional[Any] = None
    aerodynamic_spin_moment: Optional[Any] = None
    alpha1: Optional[Any] = None
    alpha2: Optional[Any] = None
    alpha3: Optional[Any] = None
    altitude: Optional[Any] = None
    angle_of_attack: Optional[Any] = None
    apogee: Optional[Any] = None
    apogee_freestream_speed: Optional[Any] = None
    apogee_state: Optional[Any] = None
    apogee_time: Optional[Any] = None
    apogee_x: Optional[Any] = None
    apogee_y: Optional[Any] = None
    atol: Optional[Any] = None
    attitude_angle: Optional[Any] = None
    attitude_frequency_response: Optional[Any] = None
    attitude_vector_x: Optional[Any] = None
    attitude_vector_y: Optional[Any] = None
    attitude_vector_z: Optional[Any] = None
    ax: Optional[Any] = None
    ay: Optional[Any] = None
    az: Optional[Any] = None
    bearing: Optional[Any] = None
    drag_power: Optional[Any] = None
    drift: Optional[Any] = None
    dynamic_pressure: Optional[Any] = None
    e0: Optional[Any] = None
    e1: Optional[Any] = None
    e2: Optional[Any] = None
    e3: Optional[Any] = None
    free_stream_speed: Optional[Any] = None
    frontal_surface_wind: Optional[Any] = None
    function_evaluations: Optional[Any] = None
    function_evaluations_per_time_step: Optional[Any] = None
    horizontal_speed: Optional[Any] = None
    impact_state: Optional[Any] = None
    impact_velocity: Optional[Any] = None
    initial_stability_margin: Optional[Any] = None
    kinetic_energy: Optional[Any] = None
    lateral_attitude_angle: Optional[Any] = None
    lateral_surface_wind: Optional[Any] = None
    mach_number: Optional[Any] = None
    max_acceleration: Optional[Any] = None
    max_acceleration_power_off: Optional[Any] = None
    max_acceleration_power_off_time: Optional[Any] = None
    max_acceleration_power_on: Optional[Any] = None
    max_acceleration_power_on_time: Optional[Any] = None
    max_acceleration_time: Optional[Any] = None
    max_dynamic_pressure: Optional[Any] = None
    max_dynamic_pressure_time: Optional[Any] = None
    max_mach_number: Optional[Any] = None
    max_mach_number_time: Optional[Any] = None
    max_rail_button1_normal_force: Optional[Any] = None
    max_rail_button1_shear_force: Optional[Any] = None
    max_rail_button2_normal_force: Optional[Any] = None
    max_rail_button2_shear_force: Optional[Any] = None
    max_reynolds_number: Optional[Any] = None
    max_reynolds_number_time: Optional[Any] = None
    max_speed: Optional[Any] = None
    max_speed_time: Optional[Any] = None
    max_stability_margin: Optional[Any] = None
    max_stability_margin_time: Optional[Any] = None
    max_total_pressure: Optional[Any] = None
    max_total_pressure_time: Optional[Any] = None
    min_stability_margin: Optional[Any] = None
    min_stability_margin_time: Optional[Any] = None
    omega1_frequency_response: Optional[Any] = None
    omega2_frequency_response: Optional[Any] = None
    omega3_frequency_response: Optional[Any] = None
    out_of_rail_stability_margin: Optional[Any] = None
    out_of_rail_state: Optional[Any] = None
    out_of_rail_velocity: Optional[Any] = None
    parachute_events: Optional[Any] = None
    path_angle: Optional[Any] = None
    phi: Optional[Any] = None
    potential_energy: Optional[Any] = None
    psi: Optional[Any] = None
    rail_button1_normal_force: Optional[Any] = None
    rail_button1_shear_force: Optional[Any] = None
    rail_button2_normal_force: Optional[Any] = None
    rail_button2_shear_force: Optional[Any] = None
    reynolds_number: Optional[Any] = None
    rotational_energy: Optional[Any] = None
    solution: Optional[Any] = None
    solution_array: Optional[Any] = None
    speed: Optional[Any] = None
    stability_margin: Optional[Any] = None
    static_margin: Optional[Any] = None
    stream_velocity_x: Optional[Any] = None
    stream_velocity_y: Optional[Any] = None
    stream_velocity_z: Optional[Any] = None
    theta: Optional[Any] = None
    thrust_power: Optional[Any] = None
    time: Optional[Any] = None
    time_steps: Optional[Any] = None
    total_energy: Optional[Any] = None
    total_pressure: Optional[Any] = None
    translational_energy: Optional[Any] = None
    vx: Optional[Any] = None
    vy: Optional[Any] = None
    vz: Optional[Any] = None
    w1: Optional[Any] = None
    w2: Optional[Any] = None
    w3: Optional[Any] = None
    x: Optional[Any] = None
    x_impact: Optional[Any] = None
    y: Optional[Any] = None
    y_impact: Optional[Any] = None
    y_sol: Optional[Any] = None
    z: Optional[Any] = None
    z_impact: Optional[Any] = None
    flight_phases: Optional[Any] = None

    model_config = ConfigDict(
        json_encoders={Any: to_python_primitive}
    )


class FlightCreated(BaseModel):
    flight_id: str
    message: str = "Flight successfully created"


class FlightUpdated(BaseModel):
    flight_id: str
    message: str = "Flight successfully updated"


class FlightDeleted(BaseModel):
    flight_id: str
    message: str = "Flight successfully deleted"


class FlightView(Flight):
    rocket: RocketView
