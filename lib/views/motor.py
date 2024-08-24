from typing import List, Any
from pydantic import BaseModel


class MotorSummary(BaseModel):
    total_burning_time: str
    total_propellant_mass: str
    average_propellant_exhaust_velocity: str
    average_thrust: str
    maximum_thrust: str
    total_impulse: str
    thrust: List[Any]
    total_mass: List[Any]
    center_of_mass: List[Any]
    i_11: List[Any]
    i_22: List[Any]
    i_33: List[Any]
    i_12: List[Any]
    i_13: List[Any]
    i_23: List[Any]


class MotorCreated(BaseModel):
    motor_id: str
    message: str = "Motor successfully created"


class MotorUpdated(BaseModel):
    motor_id: str
    message: str = "Motor successfully updated"


class MotorDeleted(BaseModel):
    motor_id: str
    message: str = "Motor successfully deleted"


class MotorPickle(BaseModel):
    jsonpickle_rocketpy_motor: str
