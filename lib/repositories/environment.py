from pymongo.results import InsertOneResult
from pymongo.results import DeleteResult
from lib.models.environment import Env
from lib.repositories.repo import Repository
from typing import Union

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

    def create_env(self) -> "InsertOneResult":
        """
        Creates a environment in the database

        Args:
            rocketpy_env: rocketpy environment object

        Returns:
            InsertOneResult: result of the insert operation
        """
        if not self.get_env():
            try:
                environment_to_dict = self.environment.dict()
                environment_to_dict["env_id"] = self.env_id
                return self.collection.insert_one(environment_to_dict)
            except:
                raise Exception("Error creating environment")
        return InsertOneResult( acknowledged=True, inserted_id=None )

    def update_env(self) -> "Union[int, None]":
        """
        Updates a environment in the database

        Returns:
            int: environment id
        """
        try:
            environment_to_dict = self.environment.dict()
            environment_to_dict["env_id"] = self.environment.__hash__()

            self.collection.update_one(
                { "env_id": self.env_id },
                { "$set": environment_to_dict }
            )

            self.env_id = environment_to_dict["env_id"]
            return self.env_id
        except:
            raise Exception("Error updating environment")

    def get_env(self) -> "Union[Env, None]":
        """
        Gets a environment from the database
        
        Returns:
            models.Env: Model environment object
        """
        try:
            environment = self.collection.find_one({ "env_id": self.env_id })
            if environment is not None:
                del environment["_id"]
                return Env.parse_obj(environment)
            return None
        except:
            raise Exception("Error getting environment")

    def delete_env(self) -> "DeleteResult":
        """
        Deletes a environment from the database

        Returns:
            DeleteResult: result of the delete operation
        """
        try:
            return self.collection.delete_one({ "env_id": self.env_id })
        except:
            raise Exception("Error deleting environment")
