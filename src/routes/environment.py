"""
Environment routes
"""

from fastapi import APIRouter, Response, Query
from opentelemetry import trace

from src.views.environment import (
    EnvironmentSimulation,
    EnvironmentCreated,
    EnvironmentRetrieved,
    EnvironmentList,
)
from src.models.environment import EnvironmentModel
from src.controllers.environment import EnvironmentController

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


@router.get("/")
async def list_environments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> EnvironmentList:
    """
    Lists environments

    ## Args
    ```
        skip: int = 0
        limit: int = 50
    ```
    """
    with tracer.start_as_current_span("list_environments"):
        controller = EnvironmentController()
        return await controller.list_environments(skip=skip, limit=limit)


@router.post("/", status_code=201)
async def create_environment(
    environment: EnvironmentModel,
) -> EnvironmentCreated:
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


@router.put("/{environment_id}", status_code=204)
async def update_environment(
    environment_id: str, environment: EnvironmentModel
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
        controller = EnvironmentController()
        return await controller.put_environment_by_id(
            environment_id, environment
        )


@router.delete("/{environment_id}", status_code=204)
async def delete_environment(environment_id: str) -> None:
    """
    Deletes an existing environment

    ## Args
    ``` environment_id: str ```
    """
    with tracer.start_as_current_span("delete_environment"):
        controller = EnvironmentController()
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
async def get_rocketpy_environment_binary(environment_id: str):
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
        controller = EnvironmentController()
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
) -> EnvironmentSimulation:
    """
    Simulates an environment

    ## Args
    ``` environment_id: Environment ID```
    """
    with tracer.start_as_current_span("get_environment_simulation"):
        controller = EnvironmentController()
        return await controller.get_environment_simulation(environment_id)
