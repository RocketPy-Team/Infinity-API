from pymongo.results import InsertOneResult
from pymongo.results import DeleteResult
from lib.models.environment import Env 
from lib.repositories.repo import Repository
from typing import Union
import jsonpickle

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

    def create_env(self, rocketpy_env) -> InsertOneResult:
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
                rocketpy_jsonpickle_hash = jsonpickle.encode(rocketpy_env)
                environment_to_dict["rocketpy_env"] = rocketpy_jsonpickle_hash
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

            updated_env = self.collection.update_one(
                { "env_id": self.env_id }, 
                { "$set": environment_to_dict }
            )

            self.env_id = environment_to_dict["env_id"]
            return  self.env_id
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
                del environment["rocketpy_env"]
                return Env.parse_obj(environment)
            else:
                return None
        except:
            raise Exception("Error getting environment")

    def get_rocketpy_env(self) -> "Union[str, None]":
        """
        Gets a rocketpy environment from the database

        Returns:
            str: rocketpy environment object encoded as a jsonpickle string hash
        """
        try:
            environment = self.collection.find_one({ "env_id": self.env_id })
            if environment is not None:
                return environment["rocketpy_env"]
            else:
                return None
        except:
            raise Exception("Error getting rocketpy environment")
    
    def delete_env(self) -> DeleteResult: 
        """
        Deletes a environment from the database

        Returns:
            DeleteResult: result of the delete operation
        """
        try: 
            return self.collection.delete_one({ "env_id": self.env_id })
        except:
            raise Exception("Error deleting environment")
