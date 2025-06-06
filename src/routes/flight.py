"""
Flight routes
"""

from fastapi import APIRouter, Response
from opentelemetry import trace

from src.views.flight import (
    FlightSimulation,
    FlightCreated,
    FlightRetrieved,
)
from src.models.environment import EnvironmentModel
from src.models.flight import FlightModel
from src.models.rocket import RocketModel
from src.controllers.flight import FlightController

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


@router.post("/", status_code=201)
async def create_flight(flight: FlightModel) -> FlightCreated:
    """
    Creates a new flight

    ## Args
    ``` models.Flight JSON ```
    """
    with tracer.start_as_current_span("create_flight"):
        controller = FlightController()
        return await controller.post_flight(flight)


@router.get("/{flight_id}")
async def read_flight(flight_id: str) -> FlightRetrieved:
    """
    Reads an existing flight

    ## Args
    ``` flight_id: str ```
    """
    with tracer.start_as_current_span("read_flight"):
        controller = FlightController()
        return await controller.get_flight_by_id(flight_id)


@router.put("/{flight_id}", status_code=204)
async def update_flight(flight_id: str, flight: FlightModel) -> None:
    """
    Updates an existing flight

    ## Args
    ```
        flight_id: str
        flight: models.flight JSON
    ```
    """
    with tracer.start_as_current_span("update_flight"):
        controller = FlightController()
        return await controller.put_flight_by_id(flight_id, flight)


@router.delete("/{flight_id}", status_code=204)
async def delete_flight(flight_id: str) -> None:
    """
    Deletes an existing flight

    ## Args
    ``` flight_id: str ```
    """
    with tracer.start_as_current_span("delete_flight"):
        controller = FlightController()
        return await controller.delete_flight_by_id(flight_id)


@router.get(
    "/{flight_id}/rocketpy",
    responses={
        200: {
            "description": "Binary file download",
            "content": {"application/octet-stream": {}},
        }
    },
    status_code=200,
    response_class=Response,
)
async def get_rocketpy_flight_binary(flight_id: str):
    """
    Loads rocketpy.flight as a dill binary.
    Currently only amd64 architecture is supported.

    ## Args
    ``` flight_id: str ```
    """
    with tracer.start_as_current_span("get_rocketpy_flight_binary"):
        controller = FlightController()
        headers = {
            'Content-Disposition': f'attachment; filename="rocketpy_flight_{flight_id}.dill"'
        }
        binary = await controller.get_rocketpy_flight_binary(flight_id)
        return Response(
            content=binary,
            headers=headers,
            media_type="application/octet-stream",
            status_code=200,
        )


@router.put("/{flight_id}/environment", status_code=204)
async def update_flight_environment(
    flight_id: str, environment: EnvironmentModel
) -> None:
    """
    Updates flight environment

    ## Args
    ```
        flight_id: Flight ID
        environment: env object as JSON
    ```
    """
    with tracer.start_as_current_span("update_flight_environment"):
        controller = FlightController()
        return await controller.update_environment_by_flight_id(
            flight_id, environment=environment
        )


@router.put("/{flight_id}/rocket", status_code=204)
async def update_flight_rocket(flight_id: str, rocket: RocketModel) -> None:
    """
    Updates flight rocket.

    ## Args
    ```
        flight_id: Flight ID
        rocket: RocketModel object as JSON
    ```
    """
    with tracer.start_as_current_span("update_flight_rocket"):
        controller = FlightController()
        return await controller.update_rocket_by_flight_id(
            flight_id,
            rocket=rocket,
        )


@router.get("/{flight_id}/simulate")
async def get_flight_simulation(flight_id: str) -> FlightSimulation:
    """
    Simulates a flight

    ## Args
    ``` flight_id: Flight ID ```
    """
    with tracer.start_as_current_span("get_flight_simulation"):
        controller = FlightController()
        return await controller.get_flight_simulation(flight_id)
