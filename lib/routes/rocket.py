"""
Rocket routes
"""

from fastapi import APIRouter

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


@router.post("/")
async def create_rocket(
    rocket: Rocket, rocket_option: RocketOptions, motor_kind: MotorKinds
) -> "RocketCreated":
    """
    Creates a new rocket

    ## Args
    ``` Rocket object as a JSON ```
    """
    return await RocketController(
        rocket, rocket_option, motor_kind
    ).create_rocket()


@router.get("/{rocket_id}")
async def read_rocket(rocket_id: int) -> Rocket:
    """
    Reads a rocket

    ## Args
    ``` rocket_id: Rocket ID hash ```
    """
    return await RocketController.get_rocket_by_id(rocket_id)


@router.put("/{rocket_id}")
async def update_rocket(
    rocket_id: int,
    rocket: Rocket,
    rocket_option: RocketOptions,
    motor_kind: MotorKinds,
) -> "RocketUpdated":
    """
    Updates a rocket

    ## Args
    ```
        rocket_id: Rocket ID hash
        rocket: Rocket object as JSON
    ```
    """
    return await RocketController(
        rocket, rocket_option, motor_kind
    ).update_rocket(rocket_id)


@router.delete("/{rocket_id}")
async def delete_rocket(rocket_id: int) -> "RocketDeleted":
    """
    Deletes a rocket

    ## Args
    ``` rocket_id: Rocket ID hash ```
    """
    return await RocketController.delete_rocket(rocket_id)


@router.get("/rocketpy/{rocket_id}")
async def read_rocketpy_rocket(rocket_id: int) -> "RocketPickle":
    """
    Reads a rocketpy rocket

    ## Args
    ``` rocket_id: Rocket ID hash ```
    """
    return await RocketController.get_rocketpy_rocket_as_jsonpickle(rocket_id)


@router.get("/{rocket_id}/simulate")
async def simulate_rocket(rocket_id: int) -> "RocketSummary":
    """
    Simulates a rocket

    ## Args
    ``` rocket_id: Rocket ID hash ```
    """
    return await RocketController.simulate_rocket(rocket_id)
