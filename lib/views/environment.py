from typing import Optional, Any
from datetime import datetime, timedelta
from pydantic import ConfigDict
from lib.views.interface import ApiBaseView
from lib.models.environment import AtmosphericModelTypes, EnvironmentModel
from lib.utils import to_python_primitive


class EnvironmentSummary(ApiBaseView):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    elevation: Optional[float] = 1
    atmospheric_model_type: Optional[str] = (
        AtmosphericModelTypes.STANDARD_ATMOSPHERE.value
    )
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
    ellipsoid: Optional[Any] = None
    barometric_height: Optional[Any] = None
    barometric_height_ISA: Optional[Any] = None
    pressure: Optional[Any] = None
    pressure_ISA: Optional[Any] = None
    temperature: Optional[Any] = None
    temperature_ISA: Optional[Any] = None
    density: Optional[Any] = None
    speed_of_sound: Optional[Any] = None
    dynamic_viscosity: Optional[Any] = None
    gravity: Optional[Any] = None
    somigliana_gravity: Optional[Any] = None
    wind_speed: Optional[Any] = None
    wind_direction: Optional[Any] = None
    wind_heading: Optional[Any] = None
    wind_velocity_x: Optional[Any] = None
    wind_velocity_y: Optional[Any] = None
    calculate_earth_radius: Optional[Any] = None
    decimal_degrees_to_arc_seconds: Optional[Any] = None
    geodesic_to_utm: Optional[Any] = None
    utm_to_geodesic: Optional[Any] = None

    model_config = ConfigDict(json_encoders={Any: to_python_primitive})


class EnvironmentView(EnvironmentModel):
    environment_id: Optional[str] = None


class EnvironmentCreated(ApiBaseView):
    message: str = "Environment successfully created"
    environment_id: str


class EnvironmentRetrieved(ApiBaseView):
    message: str = "Environment successfully retrieved"
    environment: EnvironmentView


class EnvironmentUpdated(ApiBaseView):
    message: str = "Environment successfully updated"


class EnvironmentDeleted(ApiBaseView):
    message: str = "Environment successfully deleted"
