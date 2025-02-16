from typing import Optional
from lib.models.environment import EnvironmentModel
from lib.repositories.interface import (
    RepositoryInterface,
    repository_exception_handler,
)


class EnvironmentRepository(RepositoryInterface):
    """
    Enables database CRUD operations with models.Environment

    Init Attributes:
        environment: models.EnvironmentModel
    """

    def __init__(self):
        super().__init__(EnvironmentModel)

    @repository_exception_handler
    async def create_environment(self, environment: EnvironmentModel) -> str:
        return await self.insert(environment.model_dump())

    @repository_exception_handler
    async def read_environment_by_id(
        self, environment_id: str
    ) -> Optional[EnvironmentModel]:
        return await self.find_by_id(data_id=environment_id)

    @repository_exception_handler
    async def update_environment_by_id(
        self, environment_id: str, environment: EnvironmentModel
    ):
        await self.update_by_id(
            environment.model_dump(), data_id=environment_id
        )

    @repository_exception_handler
    async def delete_environment_by_id(self, environment_id: str):
        await self.delete_by_id(data_id=environment_id)
