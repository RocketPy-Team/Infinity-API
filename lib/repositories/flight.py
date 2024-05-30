from typing import Union
from lib import logger, parse_error
from lib.models.flight import Flight
from lib.repositories.repo import Repository


class FlightRepository(Repository):
    """
    Enables database CRUD operations with models.Flight

    Init Attributes:
        flight: models.Flight
        flight_id: str

    """

    def __init__(self):
        super().__init__("flights")
        self._flight = None
        self._flight_id = None

    def fetch_flight(self, flight: Flight):
        self.flight = flight
        self.flight_id = flight.flight_id
        return self

    @property
    def flight(self) -> Flight:
        return self._flight

    @flight.setter
    def flight(self, flight: "Flight"):
        self._flight = flight

    @property
    def flight_id(self) -> str:
        return self._flight_id

    @flight_id.setter
    def flight_id(self, flight_id: "str"):
        self._flight_id = flight_id

    async def insert_flight(self, flight_data: dict):
        await self.collection.insert_one(flight_data)

    async def find_flight(self, flight_id: str):
        return await self.collection.find_one({"flight_id": flight_id})

    async def delete_flight(self, flight_id: str):
        await self.collection.delete_one({"flight_id": flight_id})
        return self

    async def create_flight(
        self, *, motor_kind: str = "SOLID", rocket_option: str = "CALISTO"
    ):
        """
        Creates a non-existing models.Flight in the database

        Args:
            rocket_option: models.rocket.RocketOptions
            motor_kind: models.motor.MotorKinds

        Returns:
            self
        """
        try:
            flight_to_dict = self.flight.dict()
            flight_to_dict["flight_id"] = self.flight_id
            flight_to_dict["rocket"]["rocket_option"] = rocket_option
            flight_to_dict["rocket"]["motor"]["motor_kind"] = motor_kind
            await self.insert_flight(flight_to_dict)
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"repositories.flight.create_flight: {exc_str}")
            raise Exception(f"Error creating flight: {exc_str}") from e
        else:
            return self
        finally:
            logger.info(
                f"Call to repositories.flight.create_flight completed for Flight {self.flight_id}"
            )

    async def get_flight_by_id(self, flight_id: str) -> Union[Flight, None]:
        """
        Gets a models.Flight from the database

        Returns:
            self
        """
        try:
            read_flight = await self.find_flight(flight_id)
            parsed_flight = (
                Flight.parse_obj(read_flight) if read_flight else None
            )
            self.flight = parsed_flight
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"repositories.flight.get_flight: {exc_str}")
            raise Exception(f"Error getting flight: {exc_str}") from e
        else:
            return self
        finally:
            logger.info(
                f"Call to repositories.flight.get_flight completed for Flight {flight_id}"
            )

    async def delete_flight_by_id(self, flight_id: str):
        """
        Deletes a models.Flight from the database

        Returns:
            self
        """
        try:
            await self.delete_flight(flight_id)
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"repositories.flight.delete_flight: {exc_str}")
            raise Exception(f"Error deleting flight: {exc_str}") from e
        else:
            return self
        finally:
            logger.info(
                f"Call to repositories.flight.delete_flight completed for Flight {flight_id}"
            )
