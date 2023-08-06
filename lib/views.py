from rocketpy import Environment, Flight
from rocketpy.prints import _FlightPrints
from pydantic import BaseModel
from typing import Optional, List, Any

class SurfaceWindConditions(BaseModel):
    frontal_surface_wind_speed: str 
    lateral_surface_wind_speed: str

class RailDepartureState(BaseModel):
    rail_departure_time: str
    rail_departure_velocity: str
    rail_departure_static_margin: str
    rail_departure_angle_of_attack: str
    rail_departure_thrust_weight_ratio: str
    rail_departure_reynolds_number: str

class BurnoutState(BaseModel):
    burnout_time: str
    altitude_at_burnout: str
    rocket_velocity_at_burnout: str
    freestream_velocity_at_burnout: str
    mach_number_at_burnout: str
    kinetic_energy_at_burnout: str

class Apogee(BaseModel):
    apogee_altitude: str
    apogee_time: str
    apogee_freestream_speed: str

class MaximumValues(BaseModel):
    maximum_speed: str
    maximum_mach_number: str
    maximum_reynolds_number: str 
    maximum_dynamic_pressure: str 
    maximum_acceleration: str 
    maximum_gs: str 
    maximum_upper_rail_button_normal_force: str
    maximum_upper_rail_button_shear_force: str 
    maximum_lower_rail_button_normal_force: str 
    maximum_lower_rail_button_shear_force: str 

class FlightSummary(BaseModel):
    surface_wind_conditions: Optional[SurfaceWindConditions]
    rail_departure_state: Optional[RailDepartureState]
    burnout_state: Optional[BurnoutState]
    apogee: Optional[Apogee]
    maximum_values: Optional[MaximumValues]

class EnvData(BaseModel):
    #TBD: review grav type
    grav: "Any"  
    launch_rail_length: float 
    elevation: int
    modelType: str
    modelTypeMaxExpectedHeight: int
    windSpeed: float 
    windDirection: float 
    windHeading: float
    surfacePressure: float
    surfaceTemperature: float
    surfaceAirDensity: float
    surfaceSpeedOfSound: float
    launch_date: str
    lat: float
    lon: float

class EnvPlots(BaseModel):
    grid: "List[float]"
    windSpeed: "List[float]"
    windDirection: "List[float]"
    speedOfSound: "List[float]"
    density: "List[float]"
    windVelX: "List[float]"
    windVelY: "List[float]"
    pressure: "List[float]"
    temperature: "List[float]"

class EnvSummary(BaseModel):
    data: EnvData
    plots: EnvPlots

class RocketSummary(BaseModel):
    pass
