from typing import Optional
from datetime import datetime, timedelta
from lib.views.interface import ApiBaseView
from lib.models.environment import EnvironmentModel
from lib.utils import AnyToPrimitive


class EnvironmentSimulation(ApiBaseView):
    message: str = "Environment successfully simulated"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    elevation: Optional[float] = 1
    atmospheric_model_type: Optional[str] = None
    air_gas_constant: Optional[float] = None
    standard_g: Optional[float] = None
    earth_radius: Optional[float] = None
    datum: Optional[str] = None
    timezone: Optional[str] = None
    initial_utm_zone: Optional[int] = None
    initial_utm_letter: Optional[str] = None
    initial_north: Optional[float] = None
    initial_east: Optional[float] = None
    initial_hemisphere: Optional[str] = None
    initial_ew: Optional[str] = None
    max_expected_height: Optional[int] = None
    date: Optional[datetime] = datetime.today() + timedelta(days=1)
    local_date: Optional[datetime] = datetime.today() + timedelta(days=1)
    datetime_date: Optional[datetime] = datetime.today() + timedelta(days=1)
    ellipsoid: Optional[AnyToPrimitive] = None
    barometric_height: Optional[AnyToPrimitive] = None
    barometric_height_ISA: Optional[AnyToPrimitive] = None
    pressure: Optional[AnyToPrimitive] = None
    pressure_ISA: Optional[AnyToPrimitive] = None
    temperature: Optional[AnyToPrimitive] = None
    temperature_ISA: Optional[AnyToPrimitive] = None
    density: Optional[AnyToPrimitive] = None
    speed_of_sound: Optional[AnyToPrimitive] = None
    dynamic_viscosity: Optional[AnyToPrimitive] = None
    gravity: Optional[AnyToPrimitive] = None
    somigliana_gravity: Optional[AnyToPrimitive] = None
    wind_speed: Optional[AnyToPrimitive] = None
    wind_direction: Optional[AnyToPrimitive] = None
    wind_heading: Optional[AnyToPrimitive] = None
    wind_velocity_x: Optional[AnyToPrimitive] = None
    wind_velocity_y: Optional[AnyToPrimitive] = None
    calculate_earth_radius: Optional[AnyToPrimitive] = None
    decimal_degrees_to_arc_seconds: Optional[AnyToPrimitive] = None
    geodesic_to_utm: Optional[AnyToPrimitive] = None
    utm_to_geodesic: Optional[AnyToPrimitive] = None


class EnvironmentView(EnvironmentModel):
    environment_id: Optional[str] = None


class EnvironmentCreated(ApiBaseView):
    message: str = "Environment successfully created"
    environment_id: str


class EnvironmentRetrieved(ApiBaseView):
    message: str = "Environment successfully retrieved"
    environment: EnvironmentView
