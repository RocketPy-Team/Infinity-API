from typing import Optional, Any, List
from pydantic import ConfigDict
from src.views.interface import ApiBaseView, PaginatedResponse
from src.models.motor import MotorModel


class MotorSimulation(ApiBaseView):
    """
    Motor simulation view that handles dynamically
    encoded RocketPy Motor attributes.

    Uses the new rocketpy_encoder which may return
    different attributes based on the actual RocketPy Motor object.
    The model allows extra fields to accommodate any
    new attributes that might be encoded.
    """

    model_config = ConfigDict(
        ser_json_exclude_none=True, extra='allow', arbitrary_types_allowed=True
    )

    message: str = "Motor successfully simulated"

    # Core Motor attributes (always present)
    burn_start_time: Optional[float] = None
    burn_out_time: Optional[float] = None
    dry_mass: Optional[float] = None
    dry_inertia: Optional[tuple] = None
    center_of_dry_mass_position: Optional[float] = None
    grains_center_of_mass_position: Optional[float] = None
    grain_number: Optional[int] = None
    grain_density: Optional[float] = None
    grain_outer_radius: Optional[float] = None
    grain_initial_inner_radius: Optional[float] = None
    grain_initial_height: Optional[float] = None
    nozzle_radius: Optional[float] = None
    throat_radius: Optional[float] = None
    nozzle_position: Optional[float] = None
    coordinate_system_orientation: Optional[str] = None
    motor_kind: Optional[str] = None
    interpolate: Optional[str] = None

    # Function attributes
    # discretized by rocketpy_encoder
    # serialized by RocketPyEncoder
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


class MotorView(MotorModel):
    motor_id: Optional[str] = None


class MotorCreated(ApiBaseView):
    message: str = "Motor successfully created"
    motor_id: str


class MotorRetrieved(ApiBaseView):
    message: str = "Motor successfully retrieved"
    motor: MotorView


class MotorList(PaginatedResponse):
    message: str = "Motors successfully retrieved"
    items: List[MotorView]
