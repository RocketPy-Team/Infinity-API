"""
Flight routes with dependency injection for improved performance.
"""

import json

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from opentelemetry import trace

from src.views.flight import (
    FlightSimulation,
    FlightCreated,
    FlightRetrieved,
    FlightImported,
)
from src.models.environment import EnvironmentModel
from src.models.flight import FlightModel, FlightWithReferencesRequest
from src.models.rocket import RocketModel
from src.dependencies import FlightControllerDep

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

MAX_RPY_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB


@router.post("/", status_code=201)
async def create_flight(
    flight: FlightModel,
    controller: FlightControllerDep,
) -> FlightCreated:
    """
    Creates a new flight

    ## Args
    ``` models.Flight JSON ```
    """
    with tracer.start_as_current_span("create_flight"):
        return await controller.post_flight(flight)


@router.post("/from-references", status_code=201)
async def create_flight_from_references(
    payload: FlightWithReferencesRequest,
    controller: FlightControllerDep,
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
        return await controller.create_flight_from_references(payload)


@router.get("/{flight_id}")
async def read_flight(
    flight_id: str,
    controller: FlightControllerDep,
) -> FlightRetrieved:
    """
    Reads an existing flight

    ## Args
    ``` flight_id: str ```
    """
    with tracer.start_as_current_span("read_flight"):
        return await controller.get_flight_by_id(flight_id)


@router.put("/{flight_id}", status_code=204)
async def update_flight(
    flight_id: str,
    flight: FlightModel,
    controller: FlightControllerDep,
) -> None:
    """
    Updates an existing flight

    ## Args
    ```
        flight_id: str
        flight: models.flight JSON
    ```
    """
    with tracer.start_as_current_span("update_flight"):
        return await controller.put_flight_by_id(flight_id, flight)


@router.put("/{flight_id}/from-references", status_code=204)
async def update_flight_from_references(
    flight_id: str,
    payload: FlightWithReferencesRequest,
    controller: FlightControllerDep,
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
        return await controller.update_flight_from_references(
            flight_id, payload
        )


@router.delete("/{flight_id}", status_code=204)
async def delete_flight(
    flight_id: str,
    controller: FlightControllerDep,
) -> None:
    """
    Deletes an existing flight

    ## Args
    ``` flight_id: str ```
    """
    with tracer.start_as_current_span("delete_flight"):
        return await controller.delete_flight_by_id(flight_id)


@router.get(
    "/{flight_id}/rocketpy",
    responses={
        200: {
            "description": "Portable .rpy JSON file download",
            "content": {"application/json": {}},
        }
    },
    status_code=200,
    response_class=Response,
)
async def get_rocketpy_flight_rpy(
    flight_id: str,
    controller: FlightControllerDep,
):
    """
    Export a rocketpy Flight as a portable ``.rpy`` JSON file.

    The ``.rpy`` format is architecture-, OS-, and
    Python-version-agnostic.

    ## Args
    ``` flight_id: str ```
    """
    with tracer.start_as_current_span("get_rocketpy_flight_rpy"):
        headers = {
            'Content-Disposition': (
                'attachment; filename=' f'"rocketpy_flight_{flight_id}.rpy"'
            ),
        }
        rpy = await controller.get_rocketpy_flight_rpy(flight_id)
        return Response(
            content=rpy,
            headers=headers,
            media_type="application/json",
            status_code=200,
        )


@router.post(
    "/upload",
    status_code=201,
    responses={
        201: {"description": "Flight imported from .rpy file"},
        413: {"description": "Uploaded .rpy file exceeds size limit"},
        422: {"description": "Invalid .rpy file"},
    },
)
async def import_flight_from_rpy(
    file: UploadFile = File(...),
    controller: FlightControllerDep = None,  # noqa: B008
) -> FlightImported:
    """
    Upload a ``.rpy`` JSON file containing a RocketPy Flight.

    The file is deserialized and decomposed into its
    constituent objects (Environment, Motor, Rocket, Flight).
    Each object is persisted as a normal JSON model and the
    corresponding IDs are returned.  Maximum upload size is 10 MB.

    ## Args
    ``` file: .rpy JSON upload ```
    """
    with tracer.start_as_current_span("import_flight_from_rpy"):
        content = await file.read(MAX_RPY_UPLOAD_BYTES + 1)
        if len(content) > MAX_RPY_UPLOAD_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Uploaded .rpy file exceeds 10 MB limit.",
            )
        return await controller.import_flight_from_rpy(content)


@router.get(
    "/{flight_id}/notebook",
    responses={
        200: {
            "description": "Jupyter notebook file download",
            "content": {"application/x-ipynb+json": {}},
        }
    },
    status_code=200,
    response_class=Response,
)
async def get_flight_notebook(
    flight_id: str,
    controller: FlightControllerDep,
):
    """
    Export a flight as a Jupyter notebook (.ipynb).

    The notebook loads the flight's ``.rpy`` file and calls
    ``flight.all_info()`` for interactive exploration.

    ## Args
    ``` flight_id: str ```
    """
    with tracer.start_as_current_span("get_flight_notebook"):
        notebook = await controller.get_flight_notebook(flight_id)
        content = json.dumps(notebook, indent=1).encode()
        filename = f"flight_{flight_id}.ipynb"
        headers = {
            "Content-Disposition": (f'attachment; filename="{filename}"'),
        }
        return Response(
            content=content,
            headers=headers,
            media_type="application/x-ipynb+json",
            status_code=200,
        )


@router.put("/{flight_id}/environment", status_code=204)
async def update_flight_environment(
    flight_id: str,
    environment: EnvironmentModel,
    controller: FlightControllerDep,
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
        return await controller.update_environment_by_flight_id(
            flight_id, environment=environment
        )


@router.put("/{flight_id}/rocket", status_code=204)
async def update_flight_rocket(
    flight_id: str,
    rocket: RocketModel,
    controller: FlightControllerDep,
) -> None:
    """
    Updates flight rocket.

    ## Args
    ```
        flight_id: Flight ID
        rocket: RocketModel object as JSON
    ```
    """
    with tracer.start_as_current_span("update_flight_rocket"):
        return await controller.update_rocket_by_flight_id(
            flight_id,
            rocket=rocket,
        )


@router.get("/{flight_id}/simulate")
async def get_flight_simulation(
    flight_id: str,
    controller: FlightControllerDep,
) -> FlightSimulation:
    """
    Simulates a flight

    ## Args
    ``` flight_id: Flight ID ```
    """
    with tracer.start_as_current_span("get_flight_simulation"):
        return await controller.get_flight_simulation(flight_id)
