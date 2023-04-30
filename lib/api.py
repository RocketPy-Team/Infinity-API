# api.py (controller)

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware

from rocketpy import Environment, Flight
from typing import Optional
from pydantic import BaseModel

from lib.models import Calisto
from lib.views import full_flight_summary 

import datetime
import json

#tbd: refactor to interface (pydantic contract) and model (interface implementation) structure
class Env(BaseModel):
    railLength: Optional[float] = 5.2
    latitude: float 
    longitude: float
    elevation: Optional[int] = 1400
    date: Optional[datetime.datetime] = datetime.datetime.today() + datetime.timedelta(days=1) 

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment
@app.post("/env/")
async def create_env(env: Env):
    env = Environment(
            railLength=env.railLength,
            latitude=env.latitude,
            longitude=env.longitude,
            elevation=env.elevation,
            date=env.date
    )
    env.setAtmosphericModel(type='StandardAtmosphere', file='GFS')
    TestFlight = Flight(rocket=Calisto, environment=env, inclination=85, heading=0)
    summary = flight_summary(TestFlight) 
    return summary

# Check app health
@app.get("/health", status_code=status.HTTP_200_OK)
def perform_healthcheck():
    return {'health': 'Everything OK!'}
