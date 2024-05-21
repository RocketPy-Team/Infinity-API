from typing import Union
from lib import logging, parse_error
from lib.models.environment import Env
from lib.repositories.repo import Repository

logger = logging.getLogger(__name__)


class EnvRepository(Repository):
    """
    Enables database CRUD operations with models.Env

    Init Attributes:
        environment: models.Env
        env_id: str

    """

    def __init__(self, environment: Env | None = None):
        super().__init__("environments")
        self._env = environment if environment else None
        self._env_id = environment.env_id if environment else None

    def __del__(self):
        self.connection.close()
        super().__del__()

    @property
    def env(self) -> Env:
        return self._env

    @env.setter
    def env(self, environment: "Env"):
        self._env = environment

    @property
    def env_id(self) -> str:
        return self._env_id

    @env_id.setter
    def env_id(self, env_id: "str"):
        self._env_id = env_id

    async def create_env(self):
        """
        Creates a non-existing models.Env in the database

        Returns:
            self
        """
        try:
            environment_to_dict = self.env.dict()
            environment_to_dict["env_id"] = self.env_id
            await self.collection.insert_one(environment_to_dict)
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"repositories.environment.create_env: {exc_str}")
            raise Exception(f"Error creating environment: {exc_str}") from e
        else:
            return self
        finally:
            logger.info(
                f"Call to repositories.environment.create_env completed for Env {self.env_id}"
            )

    async def update_env_by_id(self, env_id: str):
        """
        Updates a models.Env in the database

        Returns:
           self
        """
        try:
            environment_to_dict = self.env.dict()
            environment_to_dict["env_id"] = self.env_id
            await self.collection.update_one(
                {"env_id": env_id}, {"$set": environment_to_dict}
            )
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"repositories.environment.update_env: {exc_str}")
            raise Exception(f"Error updating environment: {exc_str}") from e
        else:
            return self
        finally:
            logger.info(
                f"Call to repositories.environment.update_env completed for Env {self.env_id}"
            )

    async def get_env_by_id(self, env_id: str) -> Union[Env, None]:
        """
        Gets a models.Env from the database

        Returns:
            models.Env
        """
        try:
            read_env = await self.collection.find_one({"env_id": env_id})
            parsed_env = Env.parse_obj(read_env) if read_env else None
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"repositories.environment.get_env: {exc_str}")
            raise Exception(f"Error getting environment: {exc_str}") from e
        else:
            return parsed_env
        finally:
            logger.info(
                f"Call to repositories.environment.get_env completed for Env {env_id}"
            )

    async def delete_env_by_id(self, env_id: str):
        """
        Deletes a models.Env from the database

        Returns:
            None
        """
        try:
            await self.collection.delete_one({"env_id": env_id})
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"repositories.environment.delete_env: {exc_str}")
            raise Exception(f"Error deleting environment: {exc_str}") from e
        finally:
            logger.info(
                f"Call to repositories.environment.delete_env completed for Env {env_id}"
            )
