from pydantic import BaseModel
from lib.models.rocket import Rocket
from lib.models.environment import Env


class Flight(BaseModel):
    environment: Env = Env()
    rocket: Rocket = Rocket()
    inclination: int = 85
    heading: int = 0
    rail_length: float = 5.2
