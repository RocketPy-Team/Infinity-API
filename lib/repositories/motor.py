from typing import Union
from pymongo.results import InsertOneResult
from pymongo.results import DeleteResult
from lib.models.motor import Motor
from lib.repositories.repo import Repository

class MotorRepository(Repository):
    """
    Motor repository

    Init Attributes:
        Motor: Motor object
        motor_id: motor id

    Enables CRUD operations on motor objects
    """

    def __init__(self, motor: Motor = None, motor_id: str = None):
        super().__init__("motors")
        self.motor = motor
        if motor_id:
            self.motor_id = motor_id
        else:
            self.motor_id = self.motor.__hash__()

    def __del__(self):
        super().__del__()

    def create_motor(self) -> "InsertOneResult":
        """
        Creates a motor in the database

        Args:
            rocketpy_Motor: rocketpy motor object

        Returns:
            InsertOneResult: result of the insert operation
        """
        if not self.get_motor():
            try:
                motor_to_dict = self.motor.dict()
                motor_to_dict["motor_id"] = self.motor_id
                return self.collection.insert_one(motor_to_dict)
            except:
                raise Exception("Error creating motor")
        return InsertOneResult( acknowledged=True, inserted_id=None )

    def update_motor(self) -> "Union[int, None]":
        """
        Updates a motor in the database

        Returns:
            int: Motor id
        """
        try:
            motor_to_dict = self.motor.dict()
            motor_to_dict["motor_id"] = self.motor.__hash__()

            updated_motor = self.collection.update_one(
                { "motor_id": self.motor_id },
                { "$set": motor_to_dict }
            )

            self.motor_id = motor_to_dict["motor_id"]
            return  self.motor_id
        except:
            raise Exception("Error updating motor")

    def get_motor(self) -> "Union[motor, None]":
        """
        Gets a motor from the database
        
        Returns:
            models.motor: Model motor object
        """
        try:
            motor = self.collection.find_one({ "motor_id": self.motor_id })
            if motor is not None:
                del motor["_id"]
                return Motor.parse_obj(motor)
            return None
        except:
            raise Exception("Error getting motor")

    def delete_motor(self) -> "DeleteResult":
        """
        Deletes a motor from the database

        Returns:
            DeleteResult: result of the delete operation
        """
        try:
            return self.collection.delete_one({ "motor_id": self.motor_id })
        except:
            raise Exception("Error deleting motor")
