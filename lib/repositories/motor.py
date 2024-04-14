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

    def __init__(self, motor: Motor = None, motor_id: str = None) -> None:
        super().__init__("motors")
        self.motor = motor
        if motor_id:
            self.motor_id = motor_id
        else:
            self.motor_id = self.motor.__hash__()

    def __del__(self):
        super().__del__()

    async def create_motor(
        self, motor_kind: str = "solid"
    ) -> "InsertOneResult":
        """
        Creates a motor in the database

        Args:
            rocketpy_Motor: rocketpy motor object

        Returns:
            InsertOneResult: result of the insert operation
        """
        if not await self.get_motor():
            try:
                motor_to_dict = self.motor.dict()
                motor_to_dict["motor_id"] = self.motor_id
                motor_to_dict["motor_kind"] = motor_kind
                return await self.collection.insert_one(motor_to_dict)
            except Exception as e:
                raise Exception(f"Error creating motor: {str(e)}") from e
            finally:
                self.__del__()
        else:
            return InsertOneResult(acknowledged=True, inserted_id=None)

    async def update_motor(
        self, motor_kind: str = "solid"
    ) -> "Union[int, None]":
        """
        Updates a motor in the database

        Returns:
            int: Motor id
        """
        try:
            motor_to_dict = self.motor.dict()
            motor_to_dict["motor_id"] = self.motor.__hash__()
            motor_to_dict["motor_kind"] = motor_kind

            await self.collection.update_one(
                {"motor_id": self.motor_id}, {"$set": motor_to_dict}
            )

            self.motor_id = motor_to_dict["motor_id"]
            return self.motor_id
        except Exception as e:
            raise Exception(f"Error updating motor: {str(e)}") from e
        finally:
            self.__del__()

    async def get_motor(self) -> "Union[motor, None]":
        """
        Gets a motor from the database

        Returns:
            models.motor: Model motor object
        """
        try:
            motor = await self.collection.find_one({"motor_id": self.motor_id})
            if motor is not None:
                return Motor.parse_obj(motor)
            return None
        except Exception as e:
            raise Exception(f"Error getting motor: {str(e)}") from e

    async def delete_motor(self) -> "DeleteResult":
        """
        Deletes a motor from the database

        Returns:
            DeleteResult: result of the delete operation
        """
        try:
            return await self.collection.delete_one(
                {"motor_id": self.motor_id}
            )
        except Exception as e:
            raise Exception(f"Error deleting motor: {str(e)}") from e
        finally:
            self.__del__()
