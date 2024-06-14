from typing import Union
from pymongo.errors import PyMongoError
from lib import logger
from lib.models.rocket import Rocket
from lib.repositories.repo import Repository, RepositoryNotInitializedException


class RocketRepository(Repository):
    """
    Enables database CRUD operations with models.Rocket

    Init Attributes:
        rocket: models.Rocket
        rocket_id: str

    """

    def __init__(self):
        super().__init__("rockets")
        self._rocket_id = None
        self._rocket = None

    def fetch_rocket(self, rocket: Rocket):
        self.rocket = rocket
        self.rocket_id = rocket.rocket_id
        return self

    @property
    def rocket(self) -> Rocket:
        return self._rocket

    @rocket.setter
    def rocket(self, rocket: "Rocket"):
        self._rocket = rocket

    @property
    def rocket_id(self) -> str:
        return self._rocket_id

    @rocket_id.setter
    def rocket_id(self, rocket_id: "str"):
        self._rocket_id = rocket_id

    async def insert_rocket(self, rocket_data: dict):
        collection = self.get_collection()
        await collection.insert_one(rocket_data)
        return self

    async def find_rocket(self, rocket_id: str):
        collection = self.get_collection()
        return await collection.find_one({"rocket_id": rocket_id})

    async def delete_rocket(self, rocket_id: str):
        collection = self.get_collection()
        await collection.delete_one({"rocket_id": rocket_id})
        return self

    async def create_rocket(
        self, *, rocket_option: str = "CALISTO", motor_kind: str = "SOLID"
    ):
        """
        Creates a non-existing models.Rocket in the database

        Args:
            rocket_option: models.rocket.RocketOptions
            motor_kind: models.motor.MotorKinds

        Returns:
            self
        """
        try:
            rocket_to_dict = self.rocket.dict()
            rocket_to_dict["rocket_id"] = self.rocket_id
            rocket_to_dict["rocket_option"] = rocket_option
            rocket_to_dict["motor"]["motor_kind"] = motor_kind
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

    async def get_rocket_by_id(self, rocket_id: str) -> Union[Rocket, None]:
        """
        Gets a models.Rocket from the database

        Returns:
            models.Rocket
        """
        try:
            read_rocket = await self.find_rocket(rocket_id)
            parsed_rocket = (
                Rocket.parse_obj(read_rocket) if read_rocket else None
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
