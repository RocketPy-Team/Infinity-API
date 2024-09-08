from typing import Self
from bson import ObjectId
from pymongo.errors import PyMongoError
from lib import logger
from lib.models.flight import Flight
from lib.models.motor import MotorKinds
from lib.repositories.repo import Repository, RepositoryNotInitializedException


class FlightRepository(Repository):
    """
    Enables database CRUD operations with models.Flight

    Init Attributes:
        flight: models.Flight
    """

    def __init__(self, flight: Flight = None):
        super().__init__("flights")
        self._flight = flight
        self._flight_id = None

    @property
    def flight(self) -> Flight:
        return self._flight

    @flight.setter
    def flight(self, flight: "Flight"):
        self._flight = flight

    @property
    def flight_id(self) -> str:
        return str(self._flight_id)

    @flight_id.setter
    def flight_id(self, flight_id: "str"):
        self._flight_id = flight_id

    async def insert_flight(self, flight_data: dict):
        collection = self.get_collection()
        result = await collection.insert_one(flight_data)
        self.flight_id = result.inserted_id
        return self

    async def update_flight(self, flight_data: dict, flight_id: str):
        collection = self.get_collection()
        await collection.update_one(
            {"_id": ObjectId(flight_id)}, {"$set": flight_data}
        )
        return self

    async def update_env(self, env_data: dict, flight_id: str):
        collection = self.get_collection()
        await collection.update_one(
            {"_id": ObjectId(flight_id)}, {"$set": {"environment": env_data}}
        )
        return self

    async def update_rocket(self, rocket_data: dict, flight_id: str):
        collection = self.get_collection()
        await collection.update_one(
            {"_id": ObjectId(flight_id)}, {"$set": {"rocket": rocket_data}}
        )
        return self

    async def find_flight(self, flight_id: str):
        collection = self.get_collection()
        return await collection.find_one({"_id": ObjectId(flight_id)})

    async def delete_flight(self, flight_id: str):
        collection = self.get_collection()
        await collection.delete_one({"_id": ObjectId(flight_id)})
        return self

    async def create_flight(self):
        """
        Creates a models.Flight in the database

        Returns:
            self
        """
        try:
            flight_to_dict = self.flight.dict()
            flight_to_dict["rocket"]["motor"][
                "motor_kind"
            ] = self.flight.rocket.motor.motor_kind.value
            await self.insert_flight(flight_to_dict)
        except PyMongoError as e:
            raise e from e
        except RepositoryNotInitializedException as e:
            raise e from e
        else:
            return self
        finally:
            logger.info(
                f"Call to repositories.flight.create_flight completed for Flight {self.flight_id}"
            )

    async def get_flight_by_id(self, flight_id: str) -> Self:
        """
        Gets a models.Flight from the database

        Returns:
            self
        """
        try:
            read_flight = await self.find_flight(flight_id)
            if read_flight:
                parsed_flight = Flight.parse_obj(read_flight)
                parsed_flight.rocket.motor.set_motor_kind(
                    MotorKinds(read_flight["rocket"]["motor"]["motor_kind"])
                )
                self.flight = parsed_flight
        except PyMongoError as e:
            raise e from e
        except RepositoryNotInitializedException as e:
            raise e from e
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
        except PyMongoError as e:
            raise e from e
        except RepositoryNotInitializedException as e:
            raise e from e
        else:
            return self
        finally:
            logger.info(
                f"Call to repositories.flight.delete_flight completed for Flight {flight_id}"
            )

    async def update_flight_by_id(self, flight_id: str):
        """
        Updates a models.Flight in the database

        Returns:
            self
        """
        try:
            flight_to_dict = self.flight.dict()
            flight_to_dict["rocket"]["motor"][
                "motor_kind"
            ] = self.flight.rocket.motor.motor_kind.value
            await self.update_flight(flight_to_dict, flight_id)
        except PyMongoError as e:
            raise e from e
        except RepositoryNotInitializedException as e:
            raise e from e
        else:
            return self
        finally:
            logger.info(
                f"Call to repositories.flight.update_flight_by_id completed for Flight {flight_id}"
            )

    async def update_env_by_flight_id(self, flight_id: str):
        """
        Updates a models.Flight.Env in the database

        Returns:
            self
        """
        try:
            env_to_dict = self.flight.environment.dict()
            await self.update_env(env_to_dict, flight_id)
        except PyMongoError as e:
            raise e from e
        except RepositoryNotInitializedException as e:
            raise e from e
        else:
            return self
        finally:
            logger.info(
                f"Call to repositories.flight.update_env_by_flight_id completed for Flight {flight_id}"
            )

    async def update_rocket_by_flight_id(self, flight_id: str):
        """
        Updates a models.Flight.Rocket in the database

        Returns:
            self
        """
        try:
            rocket_to_dict = self.flight.rocket.dict()
            rocket_to_dict["motor"][
                "motor_kind"
            ] = self.flight.rocket.motor.motor_kind.value
            await self.update_rocket(rocket_to_dict, flight_id)
        except PyMongoError as e:
            raise e from e
        except RepositoryNotInitializedException as e:
            raise e from e
        else:
            return self
        finally:
            logger.info(
                f"Call to repositories.flight.update_rocket_by_flight_id completed for Flight {flight_id}"
            )
