from pymongo.results import InsertOneResult
from pymongo.results import DeleteResult
from lib.models.rocket import Rocket 
from lib.repositories.repo import Repository
from typing import Union

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
        super().__del__()

    def create_rocket(self) -> InsertOneResult:
        """
        Creates a rocket in the database

        Args:
            rocketpy_rocket: rocketpy rocket object

        Returns:
            InsertOneResult: result of the insert operation
        """
        if not self.get_rocket():
            try: 
                rocket_to_dict = self.rocket.dict()
                rocket_to_dict["rocket_id"] = self.rocket_id 
                return self.collection.insert_one(rocket_to_dict)
            except:
                raise Exception("Error creating rocket")
        return InsertOneResult( acknowledged=True, inserted_id=None )

    def update_rocket(self) -> "Union[int, None]":
        """
        Updates a rocket in the database

        Returns:
            int: rocket id
        """
        try:
            rocket_to_dict = self.rocket.dict()
            rocket_to_dict["rocket_id"] = self.rocket.__hash__() 

            updated_rocket = self.collection.update_one(
                { "rocket_id": self.rocket_id }, 
                { "$set": rocket_to_dict }
            )

            self.rocket_id = rocket_to_dict["rocket_id"]
            return  self.rocket_id
        except:
            raise Exception("Error updating rocket")

    def get_rocket(self) -> "Union[Rocket, None]":
        """
        Gets a rocket from the database
        
        Returns:
            models.Rocket: Model rocket object
        """
        try:
            rocket = self.collection.find_one({ "rocket_id": self.rocket_id })
            if rocket is not None:
                del rocket["_id"] 
                return Rocket.parse_obj(rocket)
            else:
                return None
        except:
            raise Exception("Error getting rocket")
        
    def delete_rocket(self) -> DeleteResult: 
        """
        Deletes a rocket from the database

        Returns:
            DeleteResult: result of the delete operation
        """
        try: 
            return self.collection.delete_one({ "rocket_id": self.rocket_id })
        except:
            raise Exception("Error deleting rocket")
