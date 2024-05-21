"""
Flight routes
"""

from fastapi import APIRouter

from lib.views.flight import (
    FlightSummary,
    FlightCreated,
    FlightUpdated,
    FlightDeleted,
    FlightPickle,
)
from lib.models.environment import Env
from lib.models.flight import Flight
from lib.models.rocket import Rocket, RocketOptions
from lib.models.motor import MotorKinds
from lib.controllers.flight import FlightController

router = APIRouter(
    prefix="/flights",
    tags=["FLIGHT"],
    responses={
        404: {"description": "Not found"},
        422: {"description": "Unprocessable Entity"},
        500: {"description": "Internal Server Error"},
    },
)


@router.post("/")
async def create_flight(
    flight: Flight, rocket_option: RocketOptions, motor_kind: MotorKinds
) -> "FlightCreated":
    """
    Creates a new flight

    ## Args
    ``` Flight object as JSON ```
    """
    return await FlightController(
        flight, rocket_option, motor_kind
    ).create_flight()


@router.get("/{flight_id}")
async def read_flight(flight_id: int) -> "Flight":
    """
    Reads a flight

    ## Args
    ``` flight_id: Flight ID hash ```
    """
    return await FlightController.get_flight(flight_id)


@router.get("/rocketpy/{flight_id}")
async def read_rocketpy_flight(flight_id: int) -> "FlightPickle":
    """
    Reads a rocketpy flight object

    ## Args
    ``` flight_id: Flight ID hash. ```
    """
    return await FlightController.get_rocketpy_flight_as_jsonpickle(flight_id)


@router.put("/{flight_id}/env")
async def update_flight_env(flight_id: int, env: Env) -> "FlightUpdated":
    """
    Updates flight environment

    ## Args
    ```
        flight_id: Flight ID hash
        env: env object as JSON
    ```
    """
    return await FlightController.update_env(flight_id, env)


@router.put("/{flight_id}/rocket")
async def update_flight_rocket(
    flight_id: int,
    rocket: Rocket,
    rocket_option: RocketOptions,
    motor_kind: MotorKinds,
) -> "FlightUpdated":
    """
    Updates flight rocket.

    ## Args
    ```
        flight_id: Flight ID hash.
        rocket: Rocket object as JSON
    ```
    """
    return await FlightController.update_rocket(
        flight_id, rocket, rocket_option, motor_kind
    )


@router.put("/{flight_id}")
async def update_flight(
    flight_id: int,
    flight: Flight,
    rocket_option: RocketOptions,
    motor_kind: MotorKinds,
) -> "FlightUpdated":
    """
    Updates Flight object

    ## Args
    ```
        flight_id: Flight ID hash.
        flight: Flight object as JSON
    ```
    """
    return await FlightController(
        flight, rocket_option, motor_kind
    ).update_flight(flight_id)


@router.delete("/{flight_id}")
async def delete_flight(flight_id: int) -> "FlightDeleted":
    """
    Deletes a flight

    ## Args
    ``` flight_id: Flight ID hash ```
    """
    return await FlightController.delete_flight(flight_id)


@router.get("/{flight_id}/simulate")
async def simulate_flight(flight_id: int) -> "FlightSummary":
    """
    Simulates a flight

    ## Args
    ``` flight_id: Flight ID hash ```
    """
    return await FlightController.simulate_flight(flight_id)
