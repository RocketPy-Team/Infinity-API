from typing import Self
from bson import ObjectId
from pymongo.errors import PyMongoError
from lib import logger
from lib.models.rocket import Rocket
from lib.models.motor import MotorKinds
from lib.repositories.repo import Repository, RepositoryNotInitializedException


class RocketRepository(Repository):
    """
    Enables database CRUD operations with models.Rocket

    Init Attributes:
        rocket: models.Rocket
    """

    def __init__(self, rocket: Rocket = None):
        super().__init__("rockets")
        self._rocket_id = None
        self._rocket = rocket

    @property
    def rocket(self) -> Rocket:
        return self._rocket

    @rocket.setter
    def rocket(self, rocket: "Rocket"):
        self._rocket = rocket

    @property
    def rocket_id(self) -> str:
        return str(self._rocket_id)

    @rocket_id.setter
    def rocket_id(self, rocket_id: "str"):
        self._rocket_id = rocket_id

    async def insert_rocket(self, rocket_data: dict):
        collection = self.get_collection()
        result = await collection.insert_one(rocket_data)
        self.rocket_id = result.inserted_id
        return self

    async def update_rocket(self, rocket_data: dict, rocket_id: str):
        collection = self.get_collection()
        await collection.update_one(
            {"_id": ObjectId(rocket_id)}, {"$set": rocket_data}
        )
        return self

    async def find_rocket(self, rocket_id: str):
        collection = self.get_collection()
        return await collection.find_one({"_id": ObjectId(rocket_id)})

    async def delete_rocket(self, rocket_id: str):
        collection = self.get_collection()
        await collection.delete_one({"_id": ObjectId(rocket_id)})
        return self

    async def create_rocket(self):
        """
        Creates a models.Rocket in the database

        Returns:
            self
        """
        try:
            rocket_to_dict = self.rocket.dict()
            rocket_to_dict["motor"][
                "motor_kind"
            ] = self.rocket.motor.motor_kind.value
            await self.insert_rocket(rocket_to_dict)
        except PyMongoError as e:
            raise e from e
        except RepositoryNotInitializedException as e:
            raise e from e
        else:
            return self
        finally:
            logger.info(
                f"Call to repositories.rocket.create_rocket completed for Rocket {self.rocket_id}"
            )

    async def get_rocket_by_id(self, rocket_id: str) -> Self:
        """
        Gets a models.Rocket from the database

        Returns:
            self
        """
        try:
            read_rocket = await self.find_rocket(rocket_id)
            if read_rocket:
                parsed_rocket = Rocket.parse_obj(read_rocket)
                parsed_rocket.motor.set_motor_kind(
                    MotorKinds(read_rocket["motor"]["motor_kind"])
                )
                self.rocket = parsed_rocket
        except PyMongoError as e:
            raise e from e
        except RepositoryNotInitializedException as e:
            raise e from e
        else:
            return self
        finally:
            logger.info(
                f"Call to repositories.rocket.get_rocket completed for Rocket {rocket_id}"
            )

    async def delete_rocket_by_id(self, rocket_id: str):
        """
        Deletes a models.Rocket from the database

        Returns:
            self
        """
        try:
            await self.delete_rocket(rocket_id)
        except PyMongoError as e:
            raise e from e
        except RepositoryNotInitializedException as e:
            raise e from e
        else:
            return self
        finally:
            logger.info(
                f"Call to repositories.rocket.delete_rocket completed for Rocket {rocket_id}"
            )

    async def update_rocket_by_id(self, rocket_id: str):
        """
        Updates a models.Rocket in the database

        Returns:
            self
        """
        try:
            rocket_to_dict = self.rocket.dict()
            rocket_to_dict["motor"][
                "motor_kind"
            ] = self.rocket.motor.motor_kind.value
            await self.update_rocket(rocket_to_dict, rocket_id)
        except PyMongoError as e:
            raise e from e
        except RepositoryNotInitializedException as e:
            raise e from e
        else:
            return self
        finally:
            logger.info(
                f"Call to repositories.rocket.update_rocket_by_id completed for Rocket {rocket_id}"
            )
