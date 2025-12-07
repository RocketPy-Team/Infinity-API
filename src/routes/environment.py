"""
Environment routes
"""

from fastapi import APIRouter, Response
from opentelemetry import trace

from src.views.environment import (
    EnvironmentSimulation,
    EnvironmentCreated,
    EnvironmentRetrieved,
)
from src.models.environment import EnvironmentModel
from src.dependencies import EnvironmentControllerDep

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


@router.post("/", status_code=201)
async def create_environment(
    environment: EnvironmentModel,
    controller: EnvironmentControllerDep,
) -> EnvironmentCreated:
    """
    Creates a new environment

    ## Args
    ``` models.Environment JSON ```
    """
    with tracer.start_as_current_span("create_environment"):
        return await controller.post_environment(environment)


@router.get("/{environment_id}")
async def read_environment(
    environment_id: str,
    controller: EnvironmentControllerDep,
) -> EnvironmentRetrieved:
    """
    Reads an existing environment

    ## Args
    ``` environment_id: str ```
    """
    with tracer.start_as_current_span("read_environment"):
        return await controller.get_environment_by_id(environment_id)


@router.put("/{environment_id}", status_code=204)
async def update_environment(
    environment_id: str,
    environment: EnvironmentModel,
    controller: EnvironmentControllerDep,
) -> None:
    """
    Updates an existing environment

    ## Args
    ```
        environment_id: str
        environment: models.Environment JSON
    ```
    """
    with tracer.start_as_current_span("update_environment"):
        return await controller.put_environment_by_id(
            environment_id, environment
        )


@router.delete("/{environment_id}", status_code=204)
async def delete_environment(
    environment_id: str,
    controller: EnvironmentControllerDep,
) -> None:
    """
    Deletes an existing environment

    ## Args
    ``` environment_id: str ```
    """
    with tracer.start_as_current_span("delete_environment"):
        return await controller.delete_environment_by_id(environment_id)


@router.get(
    "/{environment_id}/rocketpy",
    responses={
        200: {
            "description": "Binary file download",
            "content": {"application/octet-stream": {}},
        }
    },
    status_code=200,
    response_class=Response,
)
async def get_rocketpy_environment_binary(
    environment_id: str,
    controller: EnvironmentControllerDep,
):
    """
    Loads rocketpy.environment as a dill binary.
    Currently only amd64 architecture is supported.

    ## Args
    ``` environment_id: str ```
    """
    with tracer.start_as_current_span("get_rocketpy_environment_binary"):
        headers = {
            'Content-Disposition': f'attachment; filename="rocketpy_environment_{environment_id}.dill"'
        }
        binary = await controller.get_rocketpy_environment_binary(
            environment_id
        )
        return Response(
            content=binary,
            headers=headers,
            media_type="application/octet-stream",
            status_code=200,
        )


@router.get("/{environment_id}/simulate")
async def get_environment_simulation(
    environment_id: str,
    controller: EnvironmentControllerDep,
) -> EnvironmentSimulation:
    """
    Simulates an environment

    ## Args
    ``` environment_id: Environment ID```
    """
    with tracer.start_as_current_span("get_environment_simulation"):
        return await controller.get_environment_simulation(environment_id)
