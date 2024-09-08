from typing import Self
from bson import ObjectId
from pymongo.errors import PyMongoError
from lib.models.environment import Env
from lib import logger
from lib.repositories.repo import Repository, RepositoryNotInitializedException


class EnvRepository(Repository):
    """
    Enables database CRUD operations with models.Env

    Init Attributes:
        environment: models.Env
    """

    def __init__(self, environment: Env = None):
        super().__init__("environments")
        self._env = environment
        self._env_id = None

    @property
    def env(self) -> Env:
        return self._env

    @env.setter
    def env(self, environment: "Env"):
        self._env = environment

    @property
    def env_id(self) -> str:
        return str(self._env_id)

    @env_id.setter
    def env_id(self, env_id: "str"):
        self._env_id = env_id

    async def insert_env(self, env_data: dict):
        collection = self.get_collection()
        result = await collection.insert_one(env_data)
        self.env_id = result.inserted_id
        return self

    async def update_env(self, env_data: dict, env_id: str):
        collection = self.get_collection()
        await collection.update_one(
            {"_id": ObjectId(env_id)}, {"$set": env_data}
        )
        return self

    async def find_env(self, env_id: str):
        collection = self.get_collection()
        return await collection.find_one({"_id": ObjectId(env_id)})

    async def delete_env(self, env_id: str):
        collection = self.get_collection()
        await collection.delete_one({"_id": ObjectId(env_id)})
        return self

    async def create_env(self):
        """
        Creates a models.Env in the database

        Returns:
            self
        """
        try:
            environment_to_dict = self.env.dict()
            await self.insert_env(environment_to_dict)
        except PyMongoError as e:
            raise e from e
        except RepositoryNotInitializedException as e:
            raise e from e
        else:
            return self
        finally:
            logger.info(
                f"Call to repositories.environment.create_env completed for Env {self.env_id}"
            )

    async def get_env_by_id(self, env_id: str) -> Self:
        """
        Gets a models.Env from the database

        Returns:
            self
        """
        try:
            read_env = await self.find_env(env_id)
            parsed_env = Env.parse_obj(read_env) if read_env else None
            self.env = parsed_env
        except PyMongoError as e:
            raise e from e
        except RepositoryNotInitializedException as e:
            raise e from e
        else:
            return self
        finally:
            logger.info(
                f"Call to repositories.environment.get_env completed for Env {env_id}"
            )

    async def delete_env_by_id(self, env_id: str):
        """
        Deletes a models.Env from the database

        Returns:
            self
        """
        try:
            await self.delete_env(env_id)
        except PyMongoError as e:
            raise e from e
        except RepositoryNotInitializedException as e:
            raise e from e
        else:
            return self
        finally:
            logger.info(
                f"Call to repositories.environment.delete_env completed for Env {env_id}"
            )

    async def update_env_by_id(self, env_id: str):
        """
        Updates a models.Env in the database

        Returns:
            self
        """
        try:
            environment_to_dict = self.env.dict()
            await self.update_env(environment_to_dict, env_id)
        except PyMongoError as e:
            raise e from e
        except RepositoryNotInitializedException as e:
            raise e from e
        else:
            return self
        finally:
            logger.info(
                f"Call to repositories.environment.update_env_by_id completed for Env {env_id}"
            )
