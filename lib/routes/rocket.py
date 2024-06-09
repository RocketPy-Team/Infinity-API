"""
Rocket routes
"""

from fastapi import APIRouter
from opentelemetry import trace

from lib.views.rocket import (
    RocketSummary,
    RocketCreated,
    RocketUpdated,
    RocketDeleted,
    RocketPickle,
)
from lib.models.rocket import Rocket, RocketOptions
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
async def create_rocket(
    rocket: Rocket, rocket_option: RocketOptions, motor_kind: MotorKinds
) -> RocketCreated:
    """
    Creates a new rocket

    ## Args
    ``` Rocket object as a JSON ```
    """
    with tracer.start_as_current_span("create_rocket"):
        return await RocketController(
            rocket=rocket, rocket_option=rocket_option, motor_kind=motor_kind
        ).create_rocket()


@router.get("/{rocket_id}")
async def read_rocket(rocket_id: str) -> Rocket:
    """
    Reads a rocket

    ## Args
    ``` rocket_id: Rocket ID hash ```
    """
    with tracer.start_as_current_span("read_rocket"):
        return await RocketController.get_rocket_by_id(rocket_id)


@router.put("/{rocket_id}")
async def update_rocket(
    rocket_id: str,
    rocket: Rocket,
    rocket_option: RocketOptions,
    motor_kind: MotorKinds,
) -> RocketUpdated:
    """
    Updates a rocket

    ## Args
    ```
        rocket_id: Rocket ID hash
        rocket: Rocket object as JSON
    ```
    """
    with tracer.start_as_current_span("update_rocket"):
        return await RocketController(
            rocket=rocket, rocket_option=rocket_option, motor_kind=motor_kind
        ).update_rocket_by_id(rocket_id)


@router.delete("/{rocket_id}")
async def delete_rocket(rocket_id: str) -> RocketDeleted:
    """
    Deletes a rocket

    ## Args
    ``` rocket_id: Rocket ID hash ```
    """
    with tracer.start_as_current_span("delete_rocket"):
        return await RocketController.delete_rocket_by_id(rocket_id)


@router.get("/rocketpy/{rocket_id}")
async def read_rocketpy_rocket(rocket_id: str) -> RocketPickle:
    """
    Reads a rocketpy rocket

    ## Args
    ``` rocket_id: Rocket ID hash ```
    """
    with tracer.start_as_current_span("read_rocketpy_rocket"):
        return await RocketController.get_rocketpy_rocket_as_jsonpickle(
            rocket_id
        )


@router.get("/{rocket_id}/simulate")
async def simulate_rocket(rocket_id: str) -> RocketSummary:
    """
    Simulates a rocket

    ## Args
    ``` rocket_id: Rocket ID hash ```
    """
    with tracer.start_as_current_span("simulate_rocket"):
        return await RocketController.simulate_rocket(rocket_id)
