from typing import Union
from lib import logging, parse_error
from lib.models.flight import Flight
from lib.repositories.repo import Repository

logger = logging.getLogger(__name__)


class FlightRepository(Repository):
    """
    Enables database CRUD operations with models.Flight

    Init Attributes:
        flight: models.Flight
        flight_id: str

    """

    def __init__(self, flight: Flight = None, flight_id: str = None):
        super().__init__("flights")
        self._flight = flight
        if flight_id:
            self._flight_id = flight_id
        else:
            self._flight_id = str(hash(self._flight))

    def __del__(self):
        self.connection.close()
        super().__del__()

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

    async def create_flight(
        self, motor_kind: str = "Solid", rocket_option: str = "Calisto"
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
            await self.collection.insert_one(flight_to_dict)
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"repositories.flight.create_flight: {exc_str}")
            raise Exception(f"Error creating flight: {str(e)}") from e
        else:
            return self
        finally:
            logger.info(
                f"Call to repositories.flight.create_flight completed for Flight {self.flight_id}"
            )

    async def update_flight(
        self, motor_kind: str = "Solid", rocket_option: str = "Calisto"
    ):
        """
        Updates a models.Flight in the database

        Returns:
            self
        """
        try:
            flight_to_dict = self.flight.dict()
            flight_to_dict["flight_id"] = str(hash(self.flight))
            flight_to_dict["rocket"]["rocket_option"] = rocket_option
            flight_to_dict["rocket"]["motor"]["motor_kind"] = motor_kind
            await self.collection.update_one(
                {"flight_id": self.flight_id}, {"$set": flight_to_dict}
            )
            self.flight_id = flight_to_dict["flight_id"]
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"repositories.flight.update_flight: {exc_str}")
            raise Exception(f"Error updating flight: {str(e)}") from e
        finally:
            logger.info(
                f"Call to repositories.flight.update_flight completed for Flight {self.flight_id}"
            )

    async def get_flight(self) -> Union[Flight, None]:
        """
        Gets a models.Flight from the database

        Returns:
            models.Flight
        """
        try:
            read_flight = await self.collection.find_one(
                {"flight_id": self.flight_id}
            )
            parsed_flight = (
                Flight.parse_obj(read_flight) if read_flight else None
            )
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"repositories.flight.get_flight: {exc_str}")
            raise Exception(f"Error getting flight: {str(e)}") from e
        else:
            return parsed_flight
        finally:
            logger.info(
                f"Call to repositories.flight.get_flight completed for Flight {self.flight_id}"
            )

    async def delete_flight(self):
        """
        Deletes a models.Flight from the database

        Returns:
            None
        """
        try:
            await self.collection.delete_one({"flight_id": self.flight_id})
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"repositories.flight.delete_flight: {exc_str}")
            raise Exception(f"Error deleting flight: {str(e)}") from e
        finally:
            logger.info(
                f"Call to repositories.flight.delete_flight completed for Flight {self.flight_id}"
            )
