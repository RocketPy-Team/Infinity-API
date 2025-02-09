from typing import Optional
from lib.models.flight import FlightModel
from lib.repositories.interface import (
    RepositoryInterface,
    repository_exception_handler,
)


class FlightRepository(RepositoryInterface):
    """
    Enables database CRUD operations with models.Flight

    Init Attributes:
        flight: models.FlightModel
    """

    def __init__(self):
        super().__init__(FlightModel)

    @repository_exception_handler
    async def create_flight(self, flight: FlightModel) -> str:
        return await self.insert(flight.model_dump())

    @repository_exception_handler
    async def read_flight_by_id(self, flight_id: str) -> Optional[FlightModel]:
        return await self.find_by_id(data_id=flight_id)

    @repository_exception_handler
    async def update_flight_by_id(self, flight_id: str, flight: FlightModel):
        await self.update_by_id(flight.model_dump(), data_id=flight_id)

    @repository_exception_handler
    async def delete_flight_by_id(self, flight_id: str):
        await self.delete_by_id(data_id=flight_id)
