"""
Rocket routes
"""

from fastapi import APIRouter, Response
from opentelemetry import trace

from lib.views.rocket import (
    RocketSummary,
    RocketCreated,
    RocketRetrieved,
    RocketUpdated,
    RocketDeleted,
)
from lib.models.rocket import RocketModel
from lib.models.motor import MotorKinds
from lib.controllers.rocket import RocketController

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


@router.post("/")
async def create_rocket(rocket: RocketModel, motor_kind: MotorKinds) -> RocketCreated:
    """
    Creates a new rocket

    ## Args
    ``` models.Rocket JSON ```
    """
    with tracer.start_as_current_span("create_rocket"):
        controller = RocketController()
        rocket.motor.set_motor_kind(motor_kind)
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


@router.put("/{rocket_id}")
async def update_rocket(rocket_id: str, rocket: RocketModel, motor_kind: MotorKinds) -> RocketUpdated:
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
        rocket.motor.set_motor_kind(motor_kind)
        return await controller.put_rocket_by_id(rocket_id, rocket)


@router.delete("/{rocket_id}")
async def delete_rocket(rocket_id: str) -> RocketDeleted:
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
        203: {
            "description": "Binary file download",
            "content": {"application/octet-stream": {}},
        }
    },
    status_code=203,
    response_class=Response,
)
async def read_rocketpy_rocket(rocket_id: str):
    """
    Loads rocketpy.rocket as a dill binary

    ## Args
    ``` rocket_id: str ```
    """
    with tracer.start_as_current_span("read_rocketpy_rocket"):
        headers = {
            'Content-Disposition': f'attachment; filename="rocketpy_rocket_{rocket_id}.dill"'
        }
        controller = RocketController()
        binary = await controller.get_rocketpy_rocket_binary(rocket_id)
        return Response(
            content=binary,
            headers=headers,
            media_type="application/octet-stream",
            status_code=203,
        )


@router.get("/{rocket_id}/summary")
async def simulate_rocket(rocket_id: str) -> RocketSummary:
    """
    Simulates a rocket

    ## Args
    ``` rocket_id: Rocket ID ```
    """
    with tracer.start_as_current_span("simulate_rocket"):
        controller = RocketController()
        return await controller.simulate_rocket(rocket_id)
