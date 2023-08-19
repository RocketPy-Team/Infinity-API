from rocketpy import Flight
from pydantic import BaseModel

class RocketData(BaseModel):

class RocketPlots(BaseModel):

class RocketSummary(BaseModel):
    data: RocketData
    plots: RocketPlots

