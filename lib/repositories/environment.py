from typing import Union
from pymongo.results import InsertOneResult
from pymongo.results import DeleteResult
from lib.models.environment import Env
from lib.repositories.repo import Repository


class EnvRepository(Repository):
    """
    Environment repository

    Init Attributes:
        environment: Env object
        env_id: Environment id

    Enables CRUD operations on environment objects
    """

    def __init__(self, environment: Env = None, env_id: str = None):
        super().__init__("environments")
        self.environment = environment
        if env_id:
            self.env_id = env_id
        else:
            self.env_id = self.environment.__hash__()

    def __del__(self):
        super().__del__()

    async def create_env(self) -> "InsertOneResult":
        """
        Creates a environment in the database

        Args:
            rocketpy_env: rocketpy environment object

        Returns:
            InsertOneResult: result of the insert operation
        """
        if not await self.get_env():
            try:
                environment_to_dict = self.environment.dict()
                environment_to_dict["env_id"] = self.env_id
                return await self.collection.insert_one(environment_to_dict)
            except Exception as e:
                raise Exception(f"Error creating environment: {str(e)}") from e
            finally:
                self.__del__()
        else:
            return InsertOneResult(acknowledged=True, inserted_id=None)

    async def update_env(self) -> "Union[int, None]":
        """
        Updates a environment in the database

        Returns:
            int: environment id
        """
        try:
            environment_to_dict = self.environment.dict()
            environment_to_dict["env_id"] = self.environment.__hash__()

            await self.collection.update_one(
                {"env_id": self.env_id}, {"$set": environment_to_dict}
            )

            self.env_id = environment_to_dict["env_id"]
            return self.env_id
        except Exception as e:
            raise Exception(f"Error updating environment: {str(e)}") from e
        finally:
            self.__del__()

    async def get_env(self) -> "Union[Env, None]":
        """
        Gets a environment from the database

        Returns:
            models.Env: Model environment object
        """
        try:
            environment = await self.collection.find_one({"env_id": self.env_id})
            if environment is not None:
                return Env.parse_obj(environment)
            return None
        except Exception as e:
            raise Exception(f"Error getting environment: {str(e)}") from e

    async def delete_env(self) -> "DeleteResult":
        """
        Deletes a environment from the database

        Returns:
            DeleteResult: result of the delete operation
        """
        try:
            return await self.collection.delete_one({"env_id": self.env_id})
        except Exception as e:
            raise Exception(f"Error deleting environment: {str(e)}") from e
        finally:
            self.__del__()
