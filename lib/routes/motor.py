"""
Motor routes
"""

from fastapi import APIRouter, Response
from opentelemetry import trace

from lib.views.motor import (
    MotorSummary,
    MotorCreated,
    MotorRetrieved,
    MotorUpdated,
    MotorDeleted,
)
from lib.models.motor import MotorModel, MotorKinds
from lib.controllers.motor import MotorController

router = APIRouter(
    prefix="/motors",
    tags=["MOTOR"],
    responses={
        404: {"description": "Not found"},
        422: {"description": "Unprocessable Entity"},
        500: {"description": "Internal Server Error"},
    },
)

tracer = trace.get_tracer(__name__)


@router.post("/")
async def create_motor(motor: MotorModel, motor_kind: MotorKinds) -> MotorCreated:
    """
    Creates a new motor

    ## Args
    ``` models.Motor JSON ```
    """
    with tracer.start_as_current_span("create_motor"):
        controller = MotorController()
        motor.set_motor_kind(motor_kind)
        return await controller.post_motor(motor)


@router.get("/{motor_id}")
async def read_motor(motor_id: str) -> MotorRetrieved:
    """
    Reads an existing motor

    ## Args
    ``` motor_id: str ```
    """
    with tracer.start_as_current_span("read_motor"):
        controller = MotorController()
        return await controller.get_motor_by_id(motor_id)


@router.put("/{motor_id}")
async def update_motor(motor_id: str, motor: MotorModel, motor_kind: MotorKinds) -> MotorUpdated:
    """
    Updates an existing motor

    ## Args
    ```
        motor_id: str
        motor: models.motor JSON
    ```
    """
    with tracer.start_as_current_span("update_motor"):
        controller = MotorController()
        motor.set_motor_kind(motor_kind)
        return await controller.put_motor_by_id(motor_id, motor)


@router.delete("/{motor_id}")
async def delete_motor(motor_id: str) -> MotorDeleted:
    """
    Deletes an existing motor

    ## Args
    ``` motor_id: str ```
    """
    with tracer.start_as_current_span("delete_motor"):
        controller = MotorController()
        return await controller.delete_motor_by_id(motor_id)


@router.get(
    "/{motor_id}/rocketpy",
    responses={
        203: {
            "description": "Binary file download",
            "content": {"application/octet-stream": {}},
        }
    },
    status_code=203,
    response_class=Response,
)
async def get_rocketpy_motor_binary(motor_id: str):
    """
    Loads rocketpy.motor as a dill binary.
    Currently only amd64 architecture is supported.

    ## Args
    ``` motor_id: str ```
    """
    with tracer.start_as_current_span("get_rocketpy_motor_binary"):
        headers = {
            'Content-Disposition': f'attachment; filename="rocketpy_motor_{motor_id}.dill"'
        }
        controller = MotorController()
        binary = await controller.get_rocketpy_motor_binary(motor_id)
        return Response(
            content=binary,
            headers=headers,
            media_type="application/octet-stream",
            status_code=203,
        )


@router.get("/{motor_id}/summary")
async def simulate_motor(motor_id: str) -> MotorSummary:
    """
    Simulates a motor

    ## Args
    ``` motor_id: Motor ID ```
    """
    with tracer.start_as_current_span("simulate_motor"):
        controller = MotorController()
        return await controller.simulate_motor(motor_id)
