from rocketpy import Environment 
from pydantic import BaseModel
from typing import List, Any

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
    env_data: EnvData
    env_plots: EnvPlots
