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

# Simulation CRUD 
## Create simulation by flight
@app.post("/simulation/flight/")
async def flight_simulation(flight: Flight):
    flight_controller = FlightController(flight)
    flight_summary = flight_controller.summary('full')
    return flight_summary

## Create simulation by environment
@app.post("/simulation/env/")
async def environment_simulation(env: Env):
    flight_controller = FlightController( Flight(environment=env) )
    flight_summary = flight_controller.summary('full')
    return flight_summary

## Read simmulation
@app.get("/simulation/{id}")
async def read_simulation(id: str):
    return "Coming soon 2!" 

## Update simulation environment 
@app.put("/simulation/env/{id}")
async def update_simulation_env(id: str, env: Env):
    return "Coming soon!" 

## Update simulation rocket 
@app.put("/simulation/rocket/{id}")
async def update_simulation_rocket(id: str, rocket: Rocket):
    return "Coming soon!" 

## Update simulation flight 
@app.put("/simulation/flight/{id}")
async def update_simulation_flight(id: str, flight: Flight):
    return "Coming soon!" 

## Delete simulation
@app.delete("/simulation/{id}")
async def delete_simulation(id: str):
    return "Coming soon!"

# Check app health
@app.get("/health", status_code=status.HTTP_200_OK)
def perform_healthcheck():
    return {'health': 'Everything OK!'}
