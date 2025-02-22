"""
Rocket routes
"""

from fastapi import APIRouter, Response
from opentelemetry import trace

from src.views.rocket import (
    RocketSimulation,
    RocketCreated,
    RocketRetrieved,
)
from src.models.rocket import RocketModel
from src.controllers.rocket import RocketController

router = APIRouter(
    prefix="/rockets",
    tags=["ROCKET"],
    responses={
        404: {"description": "Not found"},
        422: {"description": "Unprocessable Entity"},
        500: {"description": "Internal Server Error"},
    },
)

tracer = trace.get_tracer(__name__)


@router.post("/", status_code=201)
async def create_rocket(rocket: RocketModel) -> RocketCreated:
    """
    Creates a new rocket

    ## Args
    ``` models.Rocket JSON ```
    """
    with tracer.start_as_current_span("create_rocket"):
        controller = RocketController()
        return await controller.post_rocket(rocket)


@router.get("/{rocket_id}")
async def read_rocket(rocket_id: str) -> RocketRetrieved:
    """
    Reads an existing rocket

    ## Args
    ``` rocket_id: str ```
    """
    with tracer.start_as_current_span("read_rocket"):
        controller = RocketController()
        return await controller.get_rocket_by_id(rocket_id)


@router.put("/{rocket_id}", status_code=204)
async def update_rocket(rocket_id: str, rocket: RocketModel) -> None:
    """
    Updates an existing rocket

    ## Args
    ```
        rocket_id: str
        rocket: models.rocket JSON
    ```
    """
    with tracer.start_as_current_span("update_rocket"):
        controller = RocketController()
        return await controller.put_rocket_by_id(rocket_id, rocket)


@router.delete("/{rocket_id}", status_code=204)
async def delete_rocket(rocket_id: str) -> None:
    """
    Deletes an existing rocket

    ## Args
    ``` rocket_id: str ```
    """
    with tracer.start_as_current_span("delete_rocket"):
        controller = RocketController()
        return await controller.delete_rocket_by_id(rocket_id)


@router.get(
    "/{rocket_id}/rocketpy",
    responses={
        200: {
            "description": "Binary file download",
            "content": {"application/octet-stream": {}},
        }
    },
    status_code=200,
    response_class=Response,
)
async def get_rocketpy_rocket_binary(rocket_id: str):
    """
    Loads rocketpy.rocket as a dill binary.
    Currently only amd64 architecture is supported.

    ## Args
    ``` rocket_id: str ```
    """
    with tracer.start_as_current_span("get_rocketpy_rocket_binary"):
        headers = {
            'Content-Disposition': f'attachment; filename="rocketpy_rocket_{rocket_id}.dill"'
        }
        controller = RocketController()
        binary = await controller.get_rocketpy_rocket_binary(rocket_id)
        return Response(
            content=binary,
            headers=headers,
            media_type="application/octet-stream",
            status_code=200,
        )


@router.get("/{rocket_id}/simulate")
async def simulate_rocket(rocket_id: str) -> RocketSimulation:
    """
    Simulates a rocket

    ## Args
    ``` rocket_id: Rocket ID ```
    """
    with tracer.start_as_current_span("get_rocket_simulation"):
        controller = RocketController()
        return await controller.get_rocket_simulation(rocket_id)
