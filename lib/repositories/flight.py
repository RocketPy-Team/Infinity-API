from typing import Union
from pymongo.results import InsertOneResult
from pymongo.results import DeleteResult
from lib.models.flight import Flight
from lib.repositories.repo import Repository


class FlightRepository(Repository):
    """
    Flight repository

    Init Attributes:
        flight: Flight object
        flight_id: Flight id

    Enables CRUD operations on flight objects
    """

    def __init__(self, flight: Flight = None, flight_id: str = None):
        super().__init__("flights")
        self.flight = flight
        if flight_id:
            self.flight_id = flight_id
        else:
            self.flight_id = self.flight.__hash__()

    def __del__(self):
        super().__del__()

    async def create_flight(
        self, motor_kind: str = "Solid", rocket_option: str = "Calisto"
    ) -> "InsertOneResult":
        """
        Creates a flight in the database

        Args:
            rocketpy_flight: rocketpy flight object

        Returns:
            InsertOneResult: result of the insert operation
        """
        if not await self.get_flight():
            try:
                flight_to_dict = self.flight.dict()
                flight_to_dict["flight_id"] = self.flight_id
                flight_to_dict["rocket"]["rocket_option"] = rocket_option
                flight_to_dict["rocket"]["motor"]["motor_kind"] = motor_kind
                return await self.collection.insert_one(flight_to_dict)
            except Exception as e:
                raise Exception(f"Error creating flight: {str(e)}") from e
            finally:
                self.__del__()
        else:
            return InsertOneResult(acknowledged=True, inserted_id=None)

    async def update_flight(
        self, motor_kind: str = "Solid", rocket_option: str = "Calisto"
    ) -> "Union[int, None]":
        """
        Updates a flight in the database

        Returns:
            int: flight id
        """
        try:
            flight_to_dict = self.flight.dict()
            flight_to_dict["flight_id"] = self.flight.__hash__()
            flight_to_dict["rocket"]["rocket_option"] = rocket_option
            flight_to_dict["rocket"]["motor"]["motor_kind"] = motor_kind

            await self.collection.update_one(
                {"flight_id": self.flight_id}, {"$set": flight_to_dict}
            )

            self.flight_id = flight_to_dict["flight_id"]
            return self.flight_id
        except Exception as e:
            raise Exception(f"Error updating flight: {str(e)}") from e
        finally:
            self.__del__()

    async def get_flight(self) -> "Union[Flight, None]":
        """
        Gets a flight from the database

        Returns:
            models.Flight: Model flight object
        """
        try:
            flight = await self.collection.find_one(
                {"flight_id": self.flight_id}
            )
            if flight is not None:
                return Flight.parse_obj(flight)
            return None
        except Exception as e:
            raise Exception(f"Error getting flight: {str(e)}") from e

    async def delete_flight(self) -> "DeleteResult":
        """
        Deletes a flight from the database

        Returns:
            DeleteResult: result of the delete operation
        """
        try:
            return await self.collection.delete_one(
                {"flight_id": self.flight_id}
            )
        except Exception as e:
            raise Exception(f"Error deleting flight: {str(e)}") from e
        finally:
            self.__del__()
