from typing import Optional, Any
from pydantic import ConfigDict
from src.models.flight import FlightModel
from src.views.interface import ApiBaseView
from src.views.rocket import RocketView, RocketSimulation
from src.views.environment import EnvironmentSimulation


class FlightSimulation(RocketSimulation, EnvironmentSimulation):
    """
    Flight simulation view that handles dynamically encoded
    RocketPy Flight attributes.

    Inherits from both RocketSimulation and EnvironmentSimulation,
    and adds flight-specific attributes. Uses the new rocketpy_encoder
    which may return different attributes based on the actual
    RocketPy Flight object. The model allows extra fields to accommodate
    any new attributes that might be encoded.
    """

    model_config = ConfigDict(extra='allow', arbitrary_types_allowed=True)

    message: str = "Flight successfully simulated"

    # Core Flight attributes (always present)
    rail_length: Optional[float] = None
    inclination: Optional[float] = None
    heading: Optional[float] = None
    terminate_on_apogee: Optional[bool] = None
    initial_solution: Optional[list] = None
    rocket: Optional[RocketSimulation] = None
    environment: Optional[EnvironmentSimulation] = None

    # Position and trajectory
    latitude: Optional[Any] = None
    longitude: Optional[Any] = None
    altitude: Optional[Any] = None
    x: Optional[Any] = None
    y: Optional[Any] = None
    z: Optional[Any] = None

    # Velocity components
    vx: Optional[Any] = None
    vy: Optional[Any] = None
    vz: Optional[Any] = None
    speed: Optional[Any] = None

    # Key flight metrics
    apogee: Optional[Any] = None
    apogee_time: Optional[Any] = None
    apogee_x: Optional[Any] = None
    apogee_y: Optional[Any] = None
    x_impact: Optional[Any] = None
    y_impact: Optional[Any] = None
    z_impact: Optional[Any] = None
    impact_velocity: Optional[Any] = None

    # Acceleration and forces
    acceleration: Optional[Any] = None
    max_acceleration: Optional[Any] = None
    max_acceleration_time: Optional[Any] = None
    aerodynamic_drag: Optional[Any] = None
    aerodynamic_lift: Optional[Any] = None

    # Flight dynamics
    mach_number: Optional[Any] = None
    max_mach_number: Optional[Any] = None
    max_mach_number_time: Optional[Any] = None
    angle_of_attack: Optional[Any] = None
    dynamic_pressure: Optional[Any] = None
    max_dynamic_pressure: Optional[Any] = None

    # Time and simulation data
    time: Optional[Any] = None
    solution: Optional[Any] = None

    # Function attributes
    # discretized by rocketpy_encoder
    # serialized by RocketPyEncoder
    angular_position: Optional[Any] = None
    attitude_angle: Optional[Any] = None
    attitude_vector_x: Optional[Any] = None
    attitude_vector_y: Optional[Any] = None
    attitude_vector_z: Optional[Any] = None
    trajectory: Optional[Any] = None
    velocity: Optional[Any] = None
    acceleration_power_on: Optional[Any] = None
    acceleration_power_off: Optional[Any] = None
    stream_velocity: Optional[Any] = None
    free_stream_speed: Optional[Any] = None
    apogee_freestream_speed: Optional[Any] = None
    reynolds_number: Optional[Any] = None
    total_pressure: Optional[Any] = None
    rail_button_normal_force: Optional[Any] = None
    max_rail_button_normal_force: Optional[Any] = None
    rail_button_shear_force: Optional[Any] = None
    max_rail_button_shear_force: Optional[Any] = None
    rotational_energy: Optional[Any] = None
    translational_energy: Optional[Any] = None
    kinetic_energy: Optional[Any] = None
    potential_energy: Optional[Any] = None
    total_energy: Optional[Any] = None
    thrust_power: Optional[Any] = None
    drag_power: Optional[Any] = None
    drift: Optional[Any] = None


class FlightView(FlightModel):
    flight_id: str
    rocket: RocketView


class FlightCreated(ApiBaseView):
    message: str = "Flight successfully created"
    flight_id: str


class FlightRetrieved(ApiBaseView):
    message: str = "Flight successfully retrieved"
    flight: FlightView
