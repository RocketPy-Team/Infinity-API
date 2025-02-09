from typing import Optional
from lib.models.motor import MotorModel
from lib.repositories.interface import (
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
        return await self.insert(motor.model_dump())

    @repository_exception_handler
    async def read_motor_by_id(self, motor_id: str) -> Optional[MotorModel]:
        return await self.find_by_id(data_id=motor_id)

    @repository_exception_handler
    async def update_motor_by_id(self, motor_id: str, motor: MotorModel):
        await self.update_by_id(motor.model_dump(), data_id=motor_id)

    @repository_exception_handler
    async def delete_motor_by_id(self, motor_id: str):
        await self.delete_by_id(data_id=motor_id)
