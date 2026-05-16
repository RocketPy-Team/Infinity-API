"""Shared drawing-geometry view types.

Lives as its own module so both the rocket views (`src/views/rocket.py`)
and the motor views (`src/views/motor.py`) can depend on it without
creating a circular import. Nothing here is rocket- or motor-specific;
these are the raw coordinate-carrier types that rocketpy's drawing
surface produces.
"""

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


class NoseConeGeometry(BaseModel):
    model_config = ConfigDict(ser_json_exclude_none=True)
    name: Optional[str] = None
    kind: Optional[str] = None
    position: float
    x: list[float]
    y: list[float]


class TailGeometry(BaseModel):
    model_config = ConfigDict(ser_json_exclude_none=True)
    name: Optional[str] = None
    position: float
    x: list[float]
    y: list[float]


class FinOutline(BaseModel):
    x: list[float]
    y: list[float]


class FinsGeometry(BaseModel):
    model_config = ConfigDict(ser_json_exclude_none=True)
    name: Optional[str] = None
    kind: str
    n: int
    cant_angle_deg: Optional[float] = None
    position: float
    outlines: list[FinOutline]


class TubeGeometry(BaseModel):
    x_start: float
    x_end: float
    radius: float


class MotorPatch(BaseModel):
    role: Literal["nozzle", "chamber", "grain", "tank", "outline"]
    x: list[float]
    y: list[float]


class MotorDrawingGeometry(BaseModel):
    model_config = ConfigDict(ser_json_exclude_none=True)
    type: Literal["solid", "hybrid", "liquid", "empty", "generic"]
    position: float
    nozzle_position: float
    grains_center_of_mass_position: Optional[float] = None
    patches: list[MotorPatch]


class RailButtonsGeometry(BaseModel):
    lower_x: float
    upper_x: float
    y: float
    angular_position_deg: float


class SensorGeometry(BaseModel):
    model_config = ConfigDict(ser_json_exclude_none=True)
    name: Optional[str] = None
    position: tuple[float, float, float]
    normal: tuple[float, float, float]


class DrawingBounds(BaseModel):
    x_min: float
    x_max: float
    y_min: float
    y_max: float
