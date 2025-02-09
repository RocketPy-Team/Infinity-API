"""
Environment routes
"""

from fastapi import APIRouter, Response
from opentelemetry import trace

from lib.views.environment import (
    EnvironmentSummary,
    EnvironmentCreated,
    EnvironmentRetrieved,
    EnvironmentUpdated,
    EnvironmentDeleted,
)
from lib.models.environment import EnvironmentModel
from lib.controllers.environment import EnvironmentController

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
async def create_environment(environment: EnvironmentModel) -> EnvironmentCreated:
    """
    Creates a new environment

    ## Args
    ``` models.Environment JSON ```
    """
    with tracer.start_as_current_span("create_environment"):
        controller = EnvironmentController()
        return await controller.post_environment(environment)


@router.get("/{environment_id}")
async def read_environment(environment_id: str) -> EnvironmentRetrieved:
    """
    Reads an existing environment

    ## Args
    ``` environment_id: str ```
    """
    with tracer.start_as_current_span("read_environment"):
        controller = EnvironmentController()
        return await controller.get_environment_by_id(environment_id)


@router.put("/{environment_id}")
async def update_environment(environment_id: str, environment: EnvironmentModel) -> EnvironmentUpdated:
    """
    Updates an existing environment

    ## Args
    ```
        environment_id: str
        becho: models.Becho JSON
    ```
    """
    with tracer.start_as_current_span("update_becho"):
        controller = EnvironmentController()
        return await controller.put_environment_by_id(environment_id, environment)


@router.delete("/{environment_id}")
async def delete_environment(environment_id: str) -> EnvironmentDeleted:
    """
    Deletes an existing environment

    ## Args
    ``` environment_id: str ```
    """
    with tracer.start_as_current_span("delete_becho"):
        controller = EnvironmentController()
        return await controller.delete_environment_by_id(environment_id)


@router.get(
    "/{environment_id}/rocketpy",
    responses={
        203: {
            "description": "Binary file download",
            "content": {"application/octet-stream": {}},
        }
    },
    status_code=203,
    response_class=Response,
)
async def read_rocketpy_env(environment_id: str):
    """
    Loads rocketpy.environment as a dill binary

    ## Args
    ``` environment_id: str ```
    """
    with tracer.start_as_current_span("read_rocketpy_env"):
        headers = {
            'Content-Disposition': f'attachment; filename="rocketpy_environment_{environment_id}.dill"'
        }
        controller = EnvironmentController()
        binary = await controller.get_rocketpy_environment_binary(environment_id)
        return Response(
            content=binary,
            headers=headers,
            media_type="application/octet-stream",
            status_code=203,
        )


@router.get("/{environment_id}/summary")
async def simulate_env(environment_id: str) -> EnvironmentSummary:
    """
    Loads rocketpy.environment simulation

    ## Args
    ``` environment_id: str ```
    """
    with tracer.start_as_current_span("simulate_env"):
        controller = EnvironmentController()
        return await controller.get_environment_summary(environment_id)
