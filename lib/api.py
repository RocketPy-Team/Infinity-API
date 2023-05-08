# api.py

from fastapi import FastAPI, Response, status, Header
from fastapi.middleware.cors import CORSMiddleware

from lib.views import FlightSummary
from lib.models import Env, Flight, Rocket
from lib.controllers import EnvController, FlightController

from typing import Any

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Flight CRUD 
## Create flight
@app.post("/flight/")
async def create_flight(flight: Flight) -> dict[str, str]:
    successfully_created_flight = FlightController(flight).create_flight()
    return successfully_created_flight

## Read flight 
@app.get("/flight/")
async def read_flight(flight_id: int) -> Flight:
    return FlightController.get_flight(flight_id)

## Update flight environment 
@app.put("/flight/env/")
async def update_flight_env(flight_id: int, env: Env) -> dict[str, Any]:
    return FlightController.update_env(flight_id, env)

## Update flight rocket 
@app.put("/flight/rocket/")
async def update_flight_rocket(flight_id: int, rocket: Rocket) -> dict[str, Any]:
    return FlightController.update_rocket(flight_id, rocket)

## Update flight 
@app.put("/flight/")
async def update_flight(flight_id: int, flight: Flight) -> dict[str, Any]:
    return FlightController(flight).update_flight(flight_id)

## Delete flight 
@app.delete("/flight/")
async def delete_flight(flight_id: int) -> dict[str, str]:
    return FlightController.delete_flight(flight_id)

# Simmulation
## Simulate flight
@app.post("/flight/simulate/")
async def simulate_flight(flight_id: int) -> FlightSummary:
    return FlightController.simulate(flight_id)

# Check app health
@app.get("/health", status_code=status.HTTP_200_OK)
def perform_healthcheck():
    return {'health': 'Everything OK!'}
