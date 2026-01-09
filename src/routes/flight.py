"""
Flight routes
"""

from fastapi import APIRouter, Response, Query
from opentelemetry import trace

from src.views.flight import (
    FlightSimulation,
    FlightCreated,
    FlightRetrieved,
    FlightList,
)
from src.models.environment import EnvironmentModel
from src.models.flight import FlightModel, FlightWithReferencesRequest
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


@router.get("/")
async def list_flights(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> FlightList:
    """
    Lists flights

    ## Args
    ```
        skip: int = 0
        limit: int = 50
    ```
    """
    with tracer.start_as_current_span("list_flights"):
        controller = FlightController()
        return await controller.list_flights(skip=skip, limit=limit)


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


@router.post("/from-references", status_code=201)
async def create_flight_from_references(
    payload: FlightWithReferencesRequest,
) -> FlightCreated:
    """
    Creates a flight using existing rocket and environment references.

    ## Args
    ```
        environment_id: str
        rocket_id: str
        flight: Flight-only fields JSON
    ```
    """
    with tracer.start_as_current_span("create_flight_from_references"):
        controller = FlightController()
        return await controller.create_flight_from_references(payload)


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


@router.put("/{flight_id}/from-references", status_code=204)
async def update_flight_from_references(
    flight_id: str,
    payload: FlightWithReferencesRequest,
) -> None:
    """
    Updates a flight using existing rocket and environment references.

    ## Args
    ```
        flight_id: str
        environment_id: str
        rocket_id: str
        flight: Flight-only fields JSON
    ```
    """
    with tracer.start_as_current_span("update_flight_from_references"):
        controller = FlightController()
        return await controller.update_flight_from_references(
            flight_id, payload
        )


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
