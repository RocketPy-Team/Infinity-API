from rocketpy import Flight
from pydantic import BaseModel
from typing import List, Any

class MotorData(BaseModel):
    pass

class MotorSummary(BaseModel):
    data: MotorData
