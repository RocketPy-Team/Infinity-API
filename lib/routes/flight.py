"""
Flight routes
"""

from fastapi import APIRouter, Response
from opentelemetry import trace

from lib.views.flight import (
    FlightSummary,
    FlightCreated,
    FlightUpdated,
    FlightDeleted,
)
from lib.models.environment import Env
from lib.models.flight import Flight
from lib.models.rocket import Rocket
from lib.models.motor import MotorKinds
from lib.views.flight import FlightView
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

tracer = trace.get_tracer(__name__)


@router.post("/")
async def create_flight(
    flight: Flight, motor_kind: MotorKinds
) -> FlightCreated:
    """
    Creates a new flight

    ## Args
    ``` Flight object as JSON ```
    """
    with tracer.start_as_current_span("create_flight"):
        flight.rocket.motor.set_motor_kind(motor_kind)
        return await FlightController(flight).create_flight()


@router.get("/{flight_id}")
async def read_flight(flight_id: str) -> FlightView:
    """
    Reads a flight

    ## Args
    ``` flight_id: Flight ID ```
    """
    with tracer.start_as_current_span("read_flight"):
        return await FlightController.get_flight_by_id(flight_id)


@router.get(
    "/rocketpy/{flight_id}",
    responses={
        203: {
            "description": "Binary file download",
            "content": {"application/octet-stream": {}},
        }
    },
    status_code=203,
    response_class=Response,
)
async def read_rocketpy_flight(flight_id: str):
    """
    Loads rocketpy.flight as a dill binary

    ## Args
    ``` flight_id: str ```
    """
    with tracer.start_as_current_span("read_rocketpy_flight"):
        headers = {
            'Content-Disposition': f'attachment; filename="rocketpy_flight_{flight_id}.dill"'
        }
        binary = await FlightController.get_rocketpy_flight_binary(flight_id)
        return Response(
            content=binary,
            headers=headers,
            media_type="application/octet-stream",
            status_code=203,
        )


@router.put("/{flight_id}/env")
async def update_flight_env(flight_id: str, env: Env) -> FlightUpdated:
    """
    Updates flight environment

    ## Args
    ```
        flight_id: Flight ID
        env: env object as JSON
    ```
    """
    with tracer.start_as_current_span("update_flight_env"):
        return await FlightController.update_env_by_flight_id(
            flight_id, env=env
        )


@router.put("/{flight_id}/rocket")
async def update_flight_rocket(
    flight_id: str,
    rocket: Rocket,
    motor_kind: MotorKinds,
) -> FlightUpdated:
    """
    Updates flight rocket.

    ## Args
    ```
        flight_id: Flight ID
        rocket: Rocket object as JSON
    ```
    """
    with tracer.start_as_current_span("update_flight_rocket"):
        rocket.motor.set_motor_kind(motor_kind)
        return await FlightController.update_rocket_by_flight_id(
            flight_id,
            rocket=rocket,
        )


@router.put("/{flight_id}")
async def update_flight(
    flight_id: str,
    flight: Flight,
    motor_kind: MotorKinds,
) -> FlightUpdated:
    """
    Updates Flight object

    ## Args
    ```
        flight_id: Flight ID
        flight: Flight object as JSON
    ```
    """
    with tracer.start_as_current_span("update_flight"):
        flight.rocket.motor.set_motor_kind(motor_kind)
        return await FlightController(flight).update_flight_by_id(flight_id)


@router.get("/{flight_id}/summary")
async def simulate_flight(flight_id: str) -> FlightSummary:
    """
    Simulates a flight

    ## Args
    ``` flight_id: Flight ID ```
    """
    with tracer.start_as_current_span("simulate_flight"):
        return await FlightController.simulate_flight(flight_id)


@router.delete("/{flight_id}")
async def delete_flight(flight_id: str) -> FlightDeleted:
    """
    Deletes a flight

    ## Args
    ``` flight_id: Flight ID ```
    """
    with tracer.start_as_current_span("delete_flight"):
        return await FlightController.delete_flight_by_id(flight_id)
