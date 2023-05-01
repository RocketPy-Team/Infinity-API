# api.py (controller)

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware

from rocketpy import Flight
from lib.models import Calisto, Env
from lib.controllers import EnvController
from lib.views import full_flight_summary 

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
async def create_env(environment: Env):
    env=EnvController(environment)

    flight = Flight(rocket=Calisto, environment=env.env, inclination=85, heading=0)
    summary = full_flight_summary(flight) 
    return summary

# Check app health
@app.get("/health", status_code=status.HTTP_200_OK)
def perform_healthcheck():
    return {'health': 'Everything OK!'}
