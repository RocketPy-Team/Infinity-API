from pydantic import BaseModel
from lib.models.rocket import Rocket
from lib.models.environment import Env

class Flight(BaseModel, frozen=True):
    environment: Env
    rocket: Rocket
    inclination: int
    heading: int
    rail_length: float
