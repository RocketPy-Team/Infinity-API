"""
Environment routes
"""

from fastapi import APIRouter
from opentelemetry import trace

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

tracer = trace.get_tracer(__name__)


@router.post("/")
async def create_env(env: Env) -> EnvCreated:
    """
    Creates a new environment

    ## Args
    ``` models.Env JSON ```
    """
    with tracer.start_as_current_span("create_env"):
        return await EnvController(env).create_env()


@router.get("/{env_id}")
async def read_env(env_id: str) -> Env:
    """
    Reads an environment

    ## Args
    ``` env_id: str ```
    """
    with tracer.start_as_current_span("read_env"):
        return await EnvController.get_env_by_id(env_id)


@router.put("/{env_id}")
async def update_env(env_id: str, env: Env) -> EnvUpdated:
    """
    Updates an environment

    ## Args
    ```
        env_id: str
        env: models.Env JSON
    ```
    """
    with tracer.start_as_current_span("update_env"):
        return await EnvController(env).update_env_by_id(env_id)


@router.delete("/{env_id}")
async def delete_env(env_id: str) -> EnvDeleted:
    """
    Deletes an environment

    ## Args
    ``` env_id: Environment ID hash ```
    """
    with tracer.start_as_current_span("delete_env"):
        return await EnvController.delete_env_by_id(env_id)


@router.get("/rocketpy/{env_id}")
async def read_rocketpy_env(env_id: str) -> EnvPickle:
    """
    Loads rocketpy.environment as jsonpickle string

    ## Args
    ``` env_id: str ```
    """
    with tracer.start_as_current_span("read_rocketpy_env"):
        return await EnvController.get_rocketpy_env_as_jsonpickle(env_id)


@router.get("/{env_id}/simulate")
async def simulate_env(env_id: str) -> EnvSummary:
    """
    Loads rocketpy.environment simulation

    ## Args
    ``` env_id: str ```
    """
    with tracer.start_as_current_span("simulate_env"):
        return await EnvController.simulate_env(env_id)
