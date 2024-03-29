"""
Environment routes
"""
from fastapi import APIRouter

from lib.views.environment import (
    EnvSummary,
    EnvCreated,
    EnvUpdated,
    EnvDeleted,
    EnvPickle,
)
from lib.models.environment import Env
from lib.controllers.environment import EnvController

router = APIRouter(
    prefix="/environments",
    tags=["ENVIRONMENT"],
    responses={
        404: {"description": "Not found"},
        422: {"description": "Unprocessable Entity"},
        500: {"description": "Internal Server Error"},
    },
)


@router.post("/")
async def create_env(env: Env) -> "EnvCreated":
    """
    Creates a new environment

    ## Args
    ``` Env object as a JSON ```
    """
    return await EnvController(env).create_env()


@router.get("/{env_id}")
async def read_env(env_id: int) -> "Env":
    """
    Reads an environment

    ## Args
    ``` env_id: Environment ID hash ```
    """
    return await EnvController.get_env(env_id)


@router.put("/{env_id}")
async def update_env(env_id: int, env: Env) -> "EnvUpdated":
    """
    Updates an environment

    ## Args
    ```
        env_id: Environment ID hash
        env: Env object as JSON
    ```
    """
    return await EnvController(env).update_env(env_id)


@router.delete("/{env_id}")
async def delete_env(env_id: int) -> "EnvDeleted":
    """
    Deletes an environment

    ## Args
    ``` env_id: Environment ID hash ```
    """
    return await EnvController.delete_env(env_id)


@router.get("/rocketpy/{env_id}")
async def read_rocketpy_env(env_id: int) -> "EnvPickle":
    """
    Reads a rocketpy environment

    ## Args
    ``` env_id: Environment ID hash ```
    """
    return await EnvController.get_rocketpy_env(env_id)


@router.get("/{env_id}/simulate")
async def simulate_env(env_id: int) -> "EnvSummary":
    """
    Simulates an environment

    ## Args
    ``` env_id: Env ID hash ```
    """
    return await EnvController.simulate(env_id)
