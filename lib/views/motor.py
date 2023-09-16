from typing import List, Any
from pydantic import BaseModel

class MotorData(BaseModel):
    total_burning_time: str
    total_propellant_mass: str
    average_propellant_exhaust_velocity: str
    average_thrust: str
    maximum_thrust: str
    total_impulse: str

class MotorPlots(BaseModel):
    thrust: List[Any]
    total_mass: List[Any]
    center_of_mass: List[Any]
    i_11: List[Any]
    i_22: List[Any]
    i_33: List[Any]
    i_12: List[Any]
    i_13: List[Any]
    i_23: List[Any]

class MotorSummary(BaseModel):
    motor_data: MotorData
    #motor_plots: MotorPlots
