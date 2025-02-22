from typing import Optional
from src.models.flight import FlightModel
from src.views.interface import ApiBaseView
from src.views.rocket import RocketView, RocketSimulation
from src.views.environment import EnvironmentSimulation
from src.utils import AnyToPrimitive


class FlightSimulation(RocketSimulation, EnvironmentSimulation):
    message: str = "Flight successfully simulated"
    name: Optional[str] = None
    max_time: Optional[int] = None
    min_time_step: Optional[int] = None
    max_time_step: Optional[AnyToPrimitive] = None
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
    latitude: Optional[AnyToPrimitive] = None
    longitude: Optional[AnyToPrimitive] = None
    M1: Optional[AnyToPrimitive] = None
    M2: Optional[AnyToPrimitive] = None
    M3: Optional[AnyToPrimitive] = None
    R1: Optional[AnyToPrimitive] = None
    R2: Optional[AnyToPrimitive] = None
    R3: Optional[AnyToPrimitive] = None
    acceleration: Optional[AnyToPrimitive] = None
    aerodynamic_bending_moment: Optional[AnyToPrimitive] = None
    aerodynamic_drag: Optional[AnyToPrimitive] = None
    aerodynamic_lift: Optional[AnyToPrimitive] = None
    aerodynamic_spin_moment: Optional[AnyToPrimitive] = None
    alpha1: Optional[AnyToPrimitive] = None
    alpha2: Optional[AnyToPrimitive] = None
    alpha3: Optional[AnyToPrimitive] = None
    altitude: Optional[AnyToPrimitive] = None
    angle_of_attack: Optional[AnyToPrimitive] = None
    apogee: Optional[AnyToPrimitive] = None
    apogee_freestream_speed: Optional[AnyToPrimitive] = None
    apogee_state: Optional[AnyToPrimitive] = None
    apogee_time: Optional[AnyToPrimitive] = None
    apogee_x: Optional[AnyToPrimitive] = None
    apogee_y: Optional[AnyToPrimitive] = None
    atol: Optional[AnyToPrimitive] = None
    attitude_angle: Optional[AnyToPrimitive] = None
    attitude_frequency_response: Optional[AnyToPrimitive] = None
    attitude_vector_x: Optional[AnyToPrimitive] = None
    attitude_vector_y: Optional[AnyToPrimitive] = None
    attitude_vector_z: Optional[AnyToPrimitive] = None
    ax: Optional[AnyToPrimitive] = None
    ay: Optional[AnyToPrimitive] = None
    az: Optional[AnyToPrimitive] = None
    bearing: Optional[AnyToPrimitive] = None
    drag_power: Optional[AnyToPrimitive] = None
    drift: Optional[AnyToPrimitive] = None
    dynamic_pressure: Optional[AnyToPrimitive] = None
    e0: Optional[AnyToPrimitive] = None
    e1: Optional[AnyToPrimitive] = None
    e2: Optional[AnyToPrimitive] = None
    e3: Optional[AnyToPrimitive] = None
    free_stream_speed: Optional[AnyToPrimitive] = None
    frontal_surface_wind: Optional[AnyToPrimitive] = None
    function_evaluations: Optional[AnyToPrimitive] = None
    function_evaluations_per_time_step: Optional[AnyToPrimitive] = None
    horizontal_speed: Optional[AnyToPrimitive] = None
    impact_state: Optional[AnyToPrimitive] = None
    impact_velocity: Optional[AnyToPrimitive] = None
    initial_stability_margin: Optional[AnyToPrimitive] = None
    kinetic_energy: Optional[AnyToPrimitive] = None
    lateral_attitude_angle: Optional[AnyToPrimitive] = None
    lateral_surface_wind: Optional[AnyToPrimitive] = None
    mach_number: Optional[AnyToPrimitive] = None
    max_acceleration: Optional[AnyToPrimitive] = None
    max_acceleration_power_off: Optional[AnyToPrimitive] = None
    max_acceleration_power_off_time: Optional[AnyToPrimitive] = None
    max_acceleration_power_on: Optional[AnyToPrimitive] = None
    max_acceleration_power_on_time: Optional[AnyToPrimitive] = None
    max_acceleration_time: Optional[AnyToPrimitive] = None
    max_dynamic_pressure: Optional[AnyToPrimitive] = None
    max_dynamic_pressure_time: Optional[AnyToPrimitive] = None
    max_mach_number: Optional[AnyToPrimitive] = None
    max_mach_number_time: Optional[AnyToPrimitive] = None
    max_rail_button1_normal_force: Optional[AnyToPrimitive] = None
    max_rail_button1_shear_force: Optional[AnyToPrimitive] = None
    max_rail_button2_normal_force: Optional[AnyToPrimitive] = None
    max_rail_button2_shear_force: Optional[AnyToPrimitive] = None
    max_reynolds_number: Optional[AnyToPrimitive] = None
    max_reynolds_number_time: Optional[AnyToPrimitive] = None
    max_speed: Optional[AnyToPrimitive] = None
    max_speed_time: Optional[AnyToPrimitive] = None
    max_stability_margin: Optional[AnyToPrimitive] = None
    max_stability_margin_time: Optional[AnyToPrimitive] = None
    max_total_pressure: Optional[AnyToPrimitive] = None
    max_total_pressure_time: Optional[AnyToPrimitive] = None
    min_stability_margin: Optional[AnyToPrimitive] = None
    min_stability_margin_time: Optional[AnyToPrimitive] = None
    omega1_frequency_response: Optional[AnyToPrimitive] = None
    omega2_frequency_response: Optional[AnyToPrimitive] = None
    omega3_frequency_response: Optional[AnyToPrimitive] = None
    out_of_rail_stability_margin: Optional[AnyToPrimitive] = None
    out_of_rail_state: Optional[AnyToPrimitive] = None
    out_of_rail_velocity: Optional[AnyToPrimitive] = None
    parachute_events: Optional[AnyToPrimitive] = None
    path_angle: Optional[AnyToPrimitive] = None
    phi: Optional[AnyToPrimitive] = None
    potential_energy: Optional[AnyToPrimitive] = None
    psi: Optional[AnyToPrimitive] = None
    rail_button1_normal_force: Optional[AnyToPrimitive] = None
    rail_button1_shear_force: Optional[AnyToPrimitive] = None
    rail_button2_normal_force: Optional[AnyToPrimitive] = None
    rail_button2_shear_force: Optional[AnyToPrimitive] = None
    reynolds_number: Optional[AnyToPrimitive] = None
    rotational_energy: Optional[AnyToPrimitive] = None
    solution: Optional[AnyToPrimitive] = None
    solution_array: Optional[AnyToPrimitive] = None
    speed: Optional[AnyToPrimitive] = None
    stability_margin: Optional[AnyToPrimitive] = None
    static_margin: Optional[AnyToPrimitive] = None
    stream_velocity_x: Optional[AnyToPrimitive] = None
    stream_velocity_y: Optional[AnyToPrimitive] = None
    stream_velocity_z: Optional[AnyToPrimitive] = None
    theta: Optional[AnyToPrimitive] = None
    thrust_power: Optional[AnyToPrimitive] = None
    time: Optional[AnyToPrimitive] = None
    time_steps: Optional[AnyToPrimitive] = None
    total_energy: Optional[AnyToPrimitive] = None
    total_pressure: Optional[AnyToPrimitive] = None
    translational_energy: Optional[AnyToPrimitive] = None
    vx: Optional[AnyToPrimitive] = None
    vy: Optional[AnyToPrimitive] = None
    vz: Optional[AnyToPrimitive] = None
    w1: Optional[AnyToPrimitive] = None
    w2: Optional[AnyToPrimitive] = None
    w3: Optional[AnyToPrimitive] = None
    x: Optional[AnyToPrimitive] = None
    x_impact: Optional[AnyToPrimitive] = None
    y: Optional[AnyToPrimitive] = None
    y_impact: Optional[AnyToPrimitive] = None
    y_sol: Optional[AnyToPrimitive] = None
    z: Optional[AnyToPrimitive] = None
    z_impact: Optional[AnyToPrimitive] = None
    flight_phases: Optional[AnyToPrimitive] = None


class FlightView(FlightModel):
    flight_id: str
    rocket: RocketView


class FlightCreated(ApiBaseView):
    message: str = "Flight successfully created"
    flight_id: str


class FlightRetrieved(ApiBaseView):
    message: str = "Flight successfully retrieved"
    flight: FlightView
