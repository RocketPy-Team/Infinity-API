from rocketpy import Environment 
from pydantic import BaseModel
from typing import List, Any

class EnvData(BaseModel):
    #TBD: review grav type
    grav: "Any"  
    elevation: int
    model_type: str
    model_type_max_expected_height: int
    wind_speed: float 
    wind_direction: float 
    wind_heading: float
    surface_pressure: float
    surface_temperature: float
    surface_air_density: float
    surface_speed_of_sound: float
    launch_date: str
    lat: float
    lon: float

class EnvPlots(BaseModel):
    grid: "List[float]"
    wind_speed: "List[float]"
    wind_direction: "List[float]"
    speed_of_sound: "List[float]"
    density: "List[float]"
    wind_vel_x: "List[float]"
    wind_vel_y: "List[float]"
    pressure: "List[float]"
    temperature: "List[float]"

class EnvSummary(BaseModel):
    env_data: EnvData
    env_plots: EnvPlots
