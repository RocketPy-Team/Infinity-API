# api.py

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware

from lib.models import Env, Flight, Rocket
from lib.controllers import EnvController, FlightController

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment
@app.post("/simulation/env/")
async def simulate_env(env: Env):
    flight_controller = FlightController( Flight(environment=env) )
    flight_summary = flight_controller.summary('full')
    return flight_summary

# Flight
@app.post("/simulation/flight/")
async def simulate_flight(flight: Flight):
    flight_controller = FlightController(flight)
    flight_summary = flight_controller.summary('full')
    return flight_summary

# Rocket
@app.post("/simulation/rocket/")
async def simulate_rocket(rocket: Rocket):
    return "Coming soon!" 

# Read simmulation
@app.get("/simulation/{id}")
async def read_simulation(id: str):
    return "Coming soon!" 

# Check app health
@app.get("/health", status_code=status.HTTP_200_OK)
def perform_healthcheck():
    return {'health': 'Everything OK!'}
