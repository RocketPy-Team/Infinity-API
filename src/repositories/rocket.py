from typing import Optional
from src.models.rocket import RocketModel
from src.repositories.interface import (
    RepositoryInterface,
    repository_exception_handler,
)


class RocketRepository(RepositoryInterface):
    """
    Enables database CRUD operations with models.Rocket

    Init Attributes:
        rocket: models.RocketModel
    """

    def __init__(self):
        super().__init__(RocketModel)

    @repository_exception_handler
    async def create_rocket(self, rocket: RocketModel) -> str:
        return await self.insert(rocket.model_dump(exclude_none=True))

    @repository_exception_handler
    async def read_rocket_by_id(self, rocket_id: str) -> Optional[RocketModel]:
        return await self.find_by_id(data_id=rocket_id)

    @repository_exception_handler
    async def update_rocket_by_id(self, rocket_id: str, rocket: RocketModel):
        await self.update_by_id(
            rocket.model_dump(exclude_none=False), data_id=rocket_id
        )

    @repository_exception_handler
    async def delete_rocket_by_id(self, rocket_id: str):
        await self.delete_by_id(data_id=rocket_id)

    @repository_exception_handler
    async def list_rockets(self, skip: int, limit: int):
        return await self.find_all_paginated(skip=skip, limit=limit)
