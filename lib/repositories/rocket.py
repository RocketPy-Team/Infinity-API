from typing import Union
from pymongo.results import InsertOneResult
from pymongo.results import DeleteResult
from lib.models.rocket import Rocket
from lib.repositories.repo import Repository


class RocketRepository(Repository):
    """
    Rocket repository

    Init Attributes:
        rocket: Rocket object
        rocket_id: Rocket id

    Enables CRUD operations on rocket objects
    """

    def __init__(self, rocket: Rocket = None, rocket_id: str = None):
        super().__init__("rockets")
        self.rocket = rocket
        if rocket_id:
            self.rocket_id = rocket_id
        else:
            self.rocket_id = self.rocket.__hash__()

    def __del__(self):
        self.connection.close()
        super().__del__()

    async def create_rocket(
        self, rocket_option: str = "Calisto"
    ) -> "InsertOneResult":
        """
        Creates a rocket in the database

        Args:
            rocketpy_rocket: rocketpy rocket object

        Returns:
            InsertOneResult: result of the insert operation
        """
        if not await self.get_rocket():
            try:
                rocket_to_dict = self.rocket.dict()
                rocket_to_dict["rocket_id"] = self.rocket_id
                rocket_to_dict["rocket_option"] = rocket_option
                return await self.collection.insert_one(rocket_to_dict)
            except Exception as e:
                raise Exception(f"Error creating rocket: {str(e)}") from e
            finally:
                self.__del__()
        else:
            return InsertOneResult(acknowledged=True, inserted_id=None)

    async def update_rocket(
        self, rocket_option: str = "Calisto"
    ) -> "Union[int, None]":
        """
        Updates a rocket in the database

        Returns:
            int: rocket id
        """
        try:
            rocket_to_dict = self.rocket.dict()
            rocket_to_dict["rocket_id"] = self.rocket.__hash__()
            rocket_to_dict["rocket_option"] = rocket_option

            await self.collection.update_one(
                {"rocket_id": self.rocket_id}, {"$set": rocket_to_dict}
            )

            self.rocket_id = rocket_to_dict["rocket_id"]
            return self.rocket_id
        except Exception as e:
            raise Exception(f"Error updating rocket: {str(e)}") from e
        finally:
            self.__del__()

    async def get_rocket(self) -> "Union[Rocket, None]":
        """
        Gets a rocket from the database

        Returns:
            models.Rocket: Model rocket object
        """
        try:
            rocket = await self.collection.find_one(
                {"rocket_id": self.rocket_id}
            )
            if rocket is not None:
                return Rocket.parse_obj(rocket)
            return None
        except Exception as e:
            raise Exception(f"Error getting rocket: {str(e)}") from e

    async def delete_rocket(self) -> "DeleteResult":
        """
        Deletes a rocket from the database

        Returns:
            DeleteResult: result of the delete operation
        """
        try:
            return await self.collection.delete_one(
                {"rocket_id": self.rocket_id}
            )
        except Exception as e:
            raise Exception(f"Error deleting rocket: {str(e)}") from e
        finally:
            self.__del__()
