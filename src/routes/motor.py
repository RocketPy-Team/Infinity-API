"""
Motor routes
"""

from fastapi import APIRouter, Response, Query
from opentelemetry import trace

from src.views.motor import (
    MotorSimulation,
    MotorCreated,
    MotorRetrieved,
    MotorList,
)
from src.models.motor import MotorModel
from src.controllers.motor import MotorController

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


@router.get("/")
async def list_motors(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> MotorList:
    """
    Lists motors

    ## Args
    ```
        skip: int = 0
        limit: int = 50
    ```
    """
    with tracer.start_as_current_span("list_motors"):
        controller = MotorController()
        return await controller.list_motors(skip=skip, limit=limit)


@router.post("/", status_code=201)
async def create_motor(motor: MotorModel) -> MotorCreated:
    """
    Creates a new motor

    ## Args
    ``` models.Motor JSON ```
    """
    with tracer.start_as_current_span("create_motor"):
        controller = MotorController()
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


@router.put("/{motor_id}", status_code=204)
async def update_motor(motor_id: str, motor: MotorModel) -> None:
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
        return await controller.put_motor_by_id(motor_id, motor)


@router.delete("/{motor_id}", status_code=204)
async def delete_motor(motor_id: str) -> None:
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
        200: {
            "description": "Binary file download",
            "content": {"application/octet-stream": {}},
        }
    },
    status_code=200,
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
            status_code=200,
        )


@router.get("/{motor_id}/simulate")
async def get_motor_simulation(motor_id: str) -> MotorSimulation:
    """
    Simulates a motor

    ## Args
    ``` motor_id: Motor ID ```
    """
    with tracer.start_as_current_span("get_motor_simulation"):
        controller = MotorController()
        return await controller.get_motor_simulation(motor_id)
