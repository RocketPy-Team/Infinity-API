from typing import Any, Optional
from pydantic import BaseModel


class EnvSummary(BaseModel):
    # TODO: if Any is Callable, jumps pydantic parsing, expects a dill binary object
    latitude: Optional[float]
    longitude: Optional[float]
    elevation: Optional[float]
    atmospheric_model_type: Optional[str]
    air_gas_constant: Optional[float]
    standard_g: Optional[float]
    earth_radius: Optional[float]
    datum: Optional[str]
    timezone: Optional[str]
    initial_utm_zone: Optional[int]
    initial_utm_letter: Optional[str]
    initial_north: Optional[float]
    initial_east: Optional[float]
    initial_hemisphere: Optional[str]
    initial_ew: Optional[str]
    max_expected_height: Optional[int]
    date: Optional[Any]
    ellipsoid: Optional[Any]
    local_date: Optional[Any]
    datetime_date: Optional[Any]
    barometric_height: Optional[Any]
    barometric_height_ISA: Optional[Any]
    pressure: Optional[Any]
    pressure_ISA: Optional[Any]
    temperature: Optional[Any]
    temperature_ISA: Optional[Any]
    density: Optional[Any]
    speed_of_sound: Optional[Any]
    dynamic_viscosity: Optional[Any]
    gravity: Optional[Any]
    somigliana_gravity: Optional[Any]
    wind_speed: Optional[Any]
    wind_direction: Optional[Any]
    wind_heading: Optional[Any]
    wind_velocity_x: Optional[Any]
    wind_velocity_y: Optional[Any]
    calculate_earth_radius: Optional[Any]
    decimal_degrees_to_arc_seconds: Optional[Any]
    geodesic_to_utm: Optional[Any]
    utm_to_geodesic: Optional[Any]


class EnvCreated(BaseModel):
    env_id: str
    message: str = "Environment successfully created"


class EnvUpdated(BaseModel):
    env_id: str
    message: str = "Environment successfully updated"


class EnvDeleted(BaseModel):
    env_id: str
    message: str = "Environment successfully deleted"
