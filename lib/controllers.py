from rocketpy import Environment, Flight
from pydantic import BaseModel
from typing import TypeVar 
from lib.models import Env

class EnvController(BaseModel):
    env: TypeVar('Environment') 
    
    def __init__(self, environment: Env):
        super().__init__()
        self.env = Environment(
                    railLength=environment.railLength,
                    latitude=environment.latitude,
                    longitude=environment.longitude,
                    elevation=environment.elevation,
                    date=environment.date
        )
        
    def setATM(self, typ: str, fil: str):
        self.env.setAtmosphericModel(type=typ, file=fil)


