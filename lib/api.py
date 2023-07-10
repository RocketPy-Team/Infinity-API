"""
This is the main API file for the RocketPy API.
"""

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

@app.post("/flight/")
async def create_flight(flight: Flight) -> dict[str, str]:
    """
    Creates a new flight.

    Args:
        Pydantic flight object as a JSON request according to API docs.
    
    Returns:
        HTTP 200 { "message": "Flight created successfully.", id: flight_id_hash }
      
    Raises:
        HTTP 422 Unprocessable Entity: If API is unable to parse flight data, usually happens when some parameter is invalid, please attend to API docs request specifications.
        HTTP 500 Internal Server Error: If API is either unable to create flight in mongoDB or valid parameter type/structure provided but content is breaking the API. 
    """
    return FlightController(flight).create_flight()

@app.get("/flight/")
async def read_flight(flight_id: int) -> Flight:
    """
    Reads a flight.

    Args:
        flight_id: Flight ID hash.

    Returns:
        Pydantic flight object as JSON.

    Raises:
        HTTP 404 Not Found: If flight_id does not exist in database.
    """
    return FlightController.get_flight(flight_id)

@app.get("/flight/rocketpy/")
async def read_rocketpy_flight(flight_id: int) -> dict[str, Any]:
    """
    Reads a rocketpy flight object.

    Args:
        flight_id: Flight ID hash.

    Returns:
        RocketPy flight object encoded as a jsonpickle string.

    Raises:
        HTTP 404 Not Found: If flight_id does not exist in database.
    """
    return FlightController.get_rocketpy_flight(flight_id)

@app.put("/flight/env/")
async def update_flight_env(flight_id: int, env: Env) -> dict[str, Any]:
    """
    Updates flight environment.

    Args:
        flight_id: Flight ID hash.
        env: Pydantic env object as JSON request according to API docs.

    Returns:
        HTTP 200 { "message": "Flight updated successfully.", new_flight_id: new_flight_id_hash }

    Raises:
        HTTP 404 Not Found: If flight_id does not exist in database.
        HTTP 422 Unprocessable Entity: If API is unable to parse env data, usually happens when some parameter is invalid, please attend to API docs request specifications.
        HTTP 500 Internal Server Error: If API is either unable to update flight in mongoDB or valid parameter type/structure provided but content is breaking the API.
    """
    return FlightController.update_env(flight_id, env)

@app.put("/flight/rocket/")
async def update_flight_rocket(flight_id: int, rocket: Rocket) -> dict[str, Any]:
    """
    Updates flight rocket.

    Args:
        flight_id: Flight ID hash.
        rocket: Pydantic rocket object as JSON request according to API docs.

    Returns:
        HTTP 200 { "message": "Flight updated successfully.", new_flight_id: new_flight_id_hash }

    Raises:
        HTTP 404 Not Found: If flight_id does not exist in database.
        HTTP 422 Unprocessable Entity: If API is unable to parse rocket data, usually happens when some parameter is invalid, please attend to API docs request specifications.
        HTTP 500 Internal Server Error: If API is either unable to update flight in mongoDB or valid parameter type/structure provided but content is breaking the API.
    """
    return FlightController.update_rocket(flight_id, rocket)

@app.put("/flight/")
async def update_flight(flight_id: int, flight: Flight) -> dict[str, Any]:
    """
    Updates whole flight.

    Args:
        flight_id: Flight ID hash.
        flight: Pydantic flight object as JSON request according to API docs.

    Returns:
        HTTP 200 { "message": "Flight updated successfully.", new_flight_id: new_flight_id_hash }

    Raises:
        HTTP 404 Not Found: If flight_id does not exist in database.
        HTTP 422 Unprocessable Entity: If API is unable to parse flight data, usually happens when some parameter is invalid, please attend to API docs request specifications.
        HTTP 500 Internal Server Error: If API is either unable to update flight in mongoDB or valid parameter type/structure provided but content is breaking the API.
    """
    return FlightController(flight).update_flight(flight_id)

@app.delete("/flight/")
async def delete_flight(flight_id: int) -> dict[str, str]:
    """
    Deletes a flight.

    Args:
        flight_id: Flight ID hash.

    Returns:
        HTTP 200 { "message": "Flight deleted successfully." }

    Raises:
        HTTP 404 Not Found: If flight_id does not exist in database.
    """
    return FlightController.delete_flight(flight_id)

@app.get("/flight/simulation/")
async def simulate_flight(flight_id: int) -> FlightSummary:
    """
    Simulates a flight.

    Args:
        flight_id: Flight ID hash.

    Returns:
        HTTP 200 pydantic flight summary object as JSON.

    Raises:
        HTTP 404 Not Found: If flight_id does not exist in database.
    """
    return FlightController.simulate(flight_id)

@app.get("/health", status_code=status.HTTP_200_OK)
async def perform_healthcheck():
    return {'health': 'Everything OK!'}
