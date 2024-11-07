"""
Environment routes
"""

from fastapi import APIRouter, Response
from opentelemetry import trace

from lib.views.environment import (
    EnvSummary,
    EnvCreated,
    EnvUpdated,
    EnvDeleted,
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
        return await EnvController.create_env(env)


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
        return await EnvController.update_env_by_id(env_id, env)


@router.get(
    "/{env_id}/rocketpy",
    responses={
        203: {
            "description": "Binary file download",
            "content": {"application/octet-stream": {}},
        }
    },
    status_code=203,
    response_class=Response,
)
async def read_rocketpy_env(env_id: str):
    """
    Loads rocketpy.environment as a dill binary

    ## Args
    ``` env_id: str ```
    """
    with tracer.start_as_current_span("read_rocketpy_env"):
        headers = {
            'Content-Disposition': f'attachment; filename="rocketpy_environment_{env_id}.dill"'
        }
        binary = await EnvController.get_rocketpy_env_binary(env_id)
        return Response(
            content=binary,
            headers=headers,
            media_type="application/octet-stream",
            status_code=203,
        )


@router.get("/{env_id}/summary")
async def simulate_env(env_id: str) -> EnvSummary:
    """
    Loads rocketpy.environment simulation

    ## Args
    ``` env_id: str ```
    """
    with tracer.start_as_current_span("simulate_env"):
        return await EnvController.simulate_env(env_id)


@router.delete("/{env_id}")
async def delete_env(env_id: str) -> EnvDeleted:
    """
    Deletes an environment

    ## Args
    ``` env_id: str ```
    """
    with tracer.start_as_current_span("delete_env"):
        return await EnvController.delete_env_by_id(env_id)
