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

class MotorCreated(BaseModel):
    motor_id: str 
    message: str = "Motor successfully created"

class MotorUpdated(BaseModel):
    new_motor_id: str 
    message: str = "Motor successfully updated"

class MotorDeleted(BaseModel):
    deleted_motor_id: str 
    message: str = "Motor successfully deleted"

class MotorPickle(BaseModel):
    jsonpickle_rocketpy_motor: str
