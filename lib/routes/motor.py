"""
Motor routes
"""

from fastapi import APIRouter, Response
from opentelemetry import trace

from lib.views.motor import (
    MotorSummary,
    MotorCreated,
    MotorUpdated,
    MotorDeleted,
)
from lib.models.motor import Motor, MotorKinds
from lib.controllers.motor import MotorController
from lib.views.motor import MotorView

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
async def create_motor(motor: Motor, motor_kind: MotorKinds) -> MotorCreated:
    """
    Creates a new motor

    ## Args
    ``` Motor object as a JSON ```
    """
    with tracer.start_as_current_span("create_motor"):
        motor.set_motor_kind(motor_kind)
        return await MotorController(motor).create_motor()


@router.get("/{motor_id}")
async def read_motor(motor_id: str) -> MotorView:
    """
    Reads a motor

    ## Args
    ``` motor_id: Motor ID ```
    """
    with tracer.start_as_current_span("read_motor"):
        return await MotorController.get_motor_by_id(motor_id)


@router.put("/{motor_id}")
async def update_motor(
    motor_id: str, motor: Motor, motor_kind: MotorKinds
) -> MotorUpdated:
    """
    Updates a motor

    ## Args
    ```
        motor_id: Motor ID
        motor: Motor object as JSON
    ```
    """
    with tracer.start_as_current_span("update_motor"):
        motor.set_motor_kind(motor_kind)
        return await MotorController(motor).update_motor_by_id(motor_id)


@router.get(
    "/rocketpy/{motor_id}",
    responses={
        203: {
            "description": "Binary file download",
            "content": {"application/octet-stream": {}},
        }
    },
    status_code=203,
    response_class=Response,
)
async def read_rocketpy_motor(motor_id: str):
    """
    Loads rocketpy.motor as a dill binary

    ## Args
    ``` motor_id: str ```
    """
    with tracer.start_as_current_span("read_rocketpy_motor"):
        headers = {
            'Content-Disposition': f'attachment; filename="rocketpy_motor_{motor_id}.dill"'
        }
        binary = await MotorController.get_rocketpy_motor_binary(motor_id)
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
        return await MotorController.simulate_motor(motor_id)


@router.delete("/{motor_id}")
async def delete_motor(motor_id: str) -> MotorDeleted:
    """
    Deletes a motor

    ## Args
    ``` motor_id: Motor ID ```
    """
    with tracer.start_as_current_span("delete_motor"):
        return await MotorController.delete_motor_by_id(motor_id)
