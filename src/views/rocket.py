from typing import Optional, Any
from pydantic import ConfigDict
from src.models.rocket import RocketModel
from src.views.interface import ApiBaseView
from src.views.motor import MotorView, MotorSimulation

# Re-export drawing types from src.views.drawing so callers that previously
# imported them from src.views.rocket (the original home) keep working.
from src.views.drawing import (
    NoseConeGeometry,
    TailGeometry,
    FinOutline,
    FinsGeometry,
    TubeGeometry,
    MotorPatch,
    MotorDrawingGeometry,
    RailButtonsGeometry,
    SensorGeometry,
    DrawingBounds,
)

__all__ = [
    "RocketSimulation",
    "RocketView",
    "RocketCreated",
    "RocketRetrieved",
    "RocketDrawingGeometry",
    "NoseConeGeometry",
    "TailGeometry",
    "FinOutline",
    "FinsGeometry",
    "TubeGeometry",
    "MotorPatch",
    "MotorDrawingGeometry",
    "RailButtonsGeometry",
    "SensorGeometry",
    "DrawingBounds",
]


class RocketSimulation(MotorSimulation):
    """
    Rocket simulation view that handles dynamically
    encoded RocketPy Rocket attributes.

    Inherits from MotorSimulation and adds rocket-specific attributes.
    Uses the new rocketpy_encoder which may return different attributes
    based on the actual RocketPy Rocket object.

    The model allows extra fields to accommodate any new attributes
    that might be encoded.
    """

    model_config = ConfigDict(
        ser_json_exclude_none=True, extra='allow', arbitrary_types_allowed=True
    )

    message: str = "Rocket successfully simulated"

    # Core Rocket attributes (always present)
    radius: Optional[float] = None
    mass: Optional[float] = None
    inertia: Optional[
        tuple[float, float, float]
        | tuple[float, float, float, float, float, float]
    ] = None
    power_off_drag: Optional[Any] = None
    power_on_drag: Optional[Any] = None
    center_of_mass_without_motor: Optional[float] = None
    coordinate_system_orientation: Optional[str] = None
    parachutes: Optional[list] = None
    motor: Optional[MotorSimulation] = None

    # Function attributes
    # discretized by rocketpy_encoder
    # serialized by RocketPyEncoder
    I_11_without_motor: Optional[Any] = None
    I_12_without_motor: Optional[Any] = None
    I_13_without_motor: Optional[Any] = None
    I_22_without_motor: Optional[Any] = None
    I_23_without_motor: Optional[Any] = None
    I_33_without_motor: Optional[Any] = None
    check_parachute_trigger: Optional[Any] = None
    com_to_cdm_function: Optional[Any] = None
    cp_position: Optional[Any] = None
    motor_center_of_mass_position: Optional[Any] = None
    nozzle_gyration_tensor: Optional[Any] = None
    reduced_mass: Optional[Any] = None
    stability_margin: Optional[Any] = None
    static_margin: Optional[Any] = None
    thrust_to_weight: Optional[Any] = None
    total_lift_coeff_der: Optional[Any] = None


class RocketView(RocketModel):
    rocket_id: Optional[str] = None
    motor: MotorView


class RocketDrawingGeometry(ApiBaseView):
    """
    Geometry payload that mirrors what ``rocketpy.Rocket.draw()`` feeds to
    matplotlib, but as raw coordinate arrays instead of a rendered figure.
    All x/y values are already in the rocket drawing frame (the csys-applied
    axial direction matches what ``_RocketPlots`` would plot).
    """

    model_config = ConfigDict(ser_json_exclude_none=True)

    message: str = "Rocket drawing geometry retrieved"
    radius: float
    csys: int
    coordinate_system_orientation: str
    nose_cones: list[NoseConeGeometry] = []
    tails: list[TailGeometry] = []
    fins: list[FinsGeometry] = []
    tubes: list[TubeGeometry] = []
    motor: Optional[MotorDrawingGeometry] = None
    rail_buttons: Optional[RailButtonsGeometry] = None
    center_of_mass: Optional[float] = None
    cp_position: Optional[float] = None
    sensors: list[SensorGeometry] = []
    bounds: DrawingBounds


class RocketCreated(ApiBaseView):
    message: str = "Rocket successfully created"
    rocket_id: str


class RocketRetrieved(ApiBaseView):
    message: str = "Rocket successfully retrieved"
    rocket: RocketView
