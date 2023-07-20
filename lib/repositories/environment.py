from pymongo.results import InsertOneResult
from pymongo.results import DeleteResult
from lib.models import Environment
from lib.repositories.repo import Repository
from typing import Union
import jsonpickle

class EnvironmentRepository(Repository):
    """
    Environment repository

    Init Attributes:
        environment: Environment object
        environment_id: Environment id

    Enables CRUD operations on environment objects
    """
        
    def __init__(self, environment: Environment = None, environment_id: str = None):
        super().__init__()
        self.environment = environment
        if environment_id:
            self.environment_id = environment_id
        else:
            self.environment_id = self.environment.__hash__()

    def __del__(self):
        super().__del__()

    def create_environment(self, rocketpy_environment) -> InsertOneResult:
        """
        Creates a environment in the database

        Args:
            rocketpy_environment: rocketpy environment object

        Returns:
            InsertOneResult: result of the insert operation
        """
        if not self.get_environment():
            try: 
                environment_to_dict = self.environment.dict()
                environment_to_dict["environment_id"] = self.environment_id 
                rocketpy_jsonpickle_hash = jsonpickle.encode(rocketpy_environment)
                environment_to_dict["rocketpy_environment"] = rocketpy_jsonpickle_hash
                return self.collection.insert_one(environment_to_dict)
            except:
                raise Exception("Error creating environment")
        return InsertOneResult( acknowledged=True, inserted_id=None )

    def update_environment(self) -> "Union[int, None]":
        """
        Updates a environment in the database

        Returns:
            int: environment id
        """
        try:
            environment_to_dict = self.environment.dict()
            environment_to_dict["environment_id"] = self.environment.__hash__() 

            updated_environment = self.collection.update_one(
                { "environment_id": self.environment_id }, 
                { "$set": environment_to_dict }
            )

            self.environment_id = environment_to_dict["environment_id"]
            return  self.environment_id
        except:
            raise Exception("Error updating environment")

    def get_environment(self) -> "Union[Environment, None]":
        """
        Gets a environment from the database
        
        Returns:
            models.Environment: Model environment object
        """
        try:
            environment = self.collection.find_one({ "environment_id": self.environment_id })
            if environment is not None:
                del environment["_id"] 
                del environment["rocketpy_environment"]
                return Environment.parse_obj(environment)
            else:
                return None
        except:
            raise Exception("Error getting environment")

    def get_rocketpy_environment(self) -> "Union[str, None]":
        """
        Gets a rocketpy environment from the database

        Returns:
            str: rocketpy environment object encoded as a jsonpickle string hash
        """
        try:
            environment = self.collection.find_one({ "environment_id": self.environment_id })
            if environment is not None:
                return environment["rocketpy_environment"]
            else:
                return None
        except:
            raise Exception("Error getting rocketpy environment")
    
    def delete_environment(self) -> DeleteResult: 
        """
        Deletes a environment from the database

        Returns:
            DeleteResult: result of the delete operation
        """
        try: 
            return self.collection.delete_one({ "environment_id": self.environment_id })
        except:
            raise Exception("Error deleting environment")
