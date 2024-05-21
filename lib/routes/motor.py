"""
Motor routes
"""

from fastapi import APIRouter

from lib.views.motor import (
    MotorSummary,
    MotorCreated,
    MotorUpdated,
    MotorDeleted,
    MotorPickle,
)
from lib.models.motor import Motor, MotorKinds
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


@router.post("/")
async def create_motor(motor: Motor, motor_kind: MotorKinds) -> "MotorCreated":
    """
    Creates a new motor

    ## Args
    ``` Motor object as a JSON ```
    """
    return await MotorController(motor, motor_kind).create_motor()


@router.get("/{motor_id}")
async def read_motor(motor_id: int) -> "Motor":
    """
    Reads a motor

    ## Args
    ``` motor_id: Motor ID hash ```
    """
    return await MotorController.get_motor(motor_id)


@router.put("/{motor_id}")
async def update_motor(
    motor_id: int, motor: Motor, motor_kind: MotorKinds
) -> "MotorUpdated":
    """
    Updates a motor

    ## Args
    ```
        motor_id: Motor ID hash
        motor: Motor object as JSON
    ```
    """
    return await MotorController(motor, motor_kind).update_motor(motor_id)


@router.delete("/{motor_id}")
async def delete_motor(motor_id: int) -> "MotorDeleted":
    """
    Deletes a motor

    ## Args
    ``` motor_id: Motor ID hash ```
    """
    return await MotorController.delete_motor(motor_id)


@router.get("/rocketpy/{motor_id}")
async def read_rocketpy_motor(motor_id: int) -> "MotorPickle":
    """
    Reads a rocketpy motor

    ## Args
    ``` motor_id: Motor ID hash ```
    """
    return await MotorController.get_rocketpy_motor_as_jsonpickle(motor_id)


@router.get("/{motor_id}/simulate")
async def simulate_motor(motor_id: int) -> "MotorSummary":
    """
    Simulates a motor

    ## Args
    ``` motor_id: Motor ID hash ```
    """
    return await MotorController.simulate_motor(motor_id)
