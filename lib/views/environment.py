from typing import List
from pydantic import BaseModel


class EnvSummary(BaseModel):
    latitude: float
    longitude: float
    elevation: float
    # date: str #datetime
    atmospheric_model_type: str
    air_gas_constant: float
    standard_g: float
    earth_radius: float
    datum: str
    timezone: str
    # ellipsoid: str # function
    initial_utm_zone: int
    initial_utm_letter: str
    initial_north: float
    initial_east: float
    initial_hemisphere: str
    initial_ew: str
    # local_date: str #datetime
    # datetime_date: str #datetime
    max_expected_height: int
    # barometric_height: str # function
    # barometric_height_ISA: str # function
    # pressure: str # function
    # pressure_ISA: str # function
    # temperature: str # function
    # temperature_ISA: str # function
    # density: str # function
    # speed_of_sound: str # function
    # dynamic_viscosity: str # function
    # gravity: str # function
    # somigliana_gravity: str # function
    # wind_speed: str # function
    # wind_direction: str # function
    # wind_heading: str # function
    # wind_velocity_x: str # function
    # wind_velocity_y: str # function
    # calculate_earth_radius: str # function
    # decimal_degrees_to_arc_seconds: str # function
    # geodesic_to_utm: str # function
    # utm_to_geodesic: str # function
    # prints: str # function
    # plots: str # function


class EnvCreated(BaseModel):
    env_id: str
    message: str = "Environment successfully created"


class EnvUpdated(BaseModel):
    new_env_id: str
    message: str = "Environment successfully updated"


class EnvDeleted(BaseModel):
    deleted_env_id: str
    message: str = "Environment successfully deleted"


class EnvPickle(BaseModel):
    jsonpickle_rocketpy_env: str
