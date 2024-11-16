"""
Rocket routes
"""

from fastapi import APIRouter, Response
from opentelemetry import trace

from lib.views.rocket import (
    RocketSummary,
    RocketCreated,
    RocketUpdated,
    RocketDeleted,
)
from lib.models.rocket import Rocket
from lib.models.motor import MotorKinds
from lib.views.rocket import RocketView
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
async def create_rocket(
    rocket: Rocket, motor_kind: MotorKinds
) -> RocketCreated:
    """
    Creates a new rocket

    ## Args
    ``` Rocket object as a JSON ```
    """
    with tracer.start_as_current_span("create_rocket"):
        rocket.motor.set_motor_kind(motor_kind)
        return await RocketController.create_rocket(rocket)


@router.get("/{rocket_id}")
async def read_rocket(rocket_id: str) -> RocketView:
    """
    Reads a rocket

    ## Args
    ``` rocket_id: Rocket ID ```
    """
    with tracer.start_as_current_span("read_rocket"):
        return await RocketController.get_rocket_by_id(rocket_id)


@router.put("/{rocket_id}")
async def update_rocket(
    rocket_id: str,
    rocket: Rocket,
    motor_kind: MotorKinds,
) -> RocketUpdated:
    """
    Updates a rocket

    ## Args
    ```
        rocket_id: Rocket ID
        rocket: Rocket object as JSON
    ```
    """
    with tracer.start_as_current_span("update_rocket"):
        rocket.motor.set_motor_kind(motor_kind)
        return await RocketController.update_rocket_by_id(rocket_id, rocket)


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
        binary = await RocketController.get_rocketpy_rocket_binary(rocket_id)
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
        return await RocketController.simulate_rocket(rocket_id)


@router.delete("/{rocket_id}")
async def delete_rocket(rocket_id: str) -> RocketDeleted:
    """
    Deletes a rocket

    ## Args
    ``` rocket_id: Rocket ID ```
    """
    with tracer.start_as_current_span("delete_rocket"):
        return await RocketController.delete_rocket_by_id(rocket_id)
