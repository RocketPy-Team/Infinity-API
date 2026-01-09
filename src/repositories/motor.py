from typing import Optional
from src.models.motor import MotorModel
from src.repositories.interface import (
    RepositoryInterface,
    repository_exception_handler,
)


class MotorRepository(RepositoryInterface):
    """
    Enables database CRUD operations with models.Motor

    Init Attributes:
        motor: models.MotorModel
    """

    def __init__(self):
        super().__init__(MotorModel)

    @repository_exception_handler
    async def create_motor(self, motor: MotorModel) -> str:
        return await self.insert(motor.model_dump(exclude_none=True))

    @repository_exception_handler
    async def read_motor_by_id(self, motor_id: str) -> Optional[MotorModel]:
        return await self.find_by_id(data_id=motor_id)

    @repository_exception_handler
    async def update_motor_by_id(self, motor_id: str, motor: MotorModel):
        await self.update_by_id(
            motor.model_dump(exclude_none=False), data_id=motor_id
        )

    @repository_exception_handler
    async def delete_motor_by_id(self, motor_id: str):
        await self.delete_by_id(data_id=motor_id)

    @repository_exception_handler
    async def list_motors(self, skip: int, limit: int):
        return await self.find_all_paginated(skip=skip, limit=limit)
