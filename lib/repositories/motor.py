from typing import Union
from bson import ObjectId
from pymongo.errors import PyMongoError
from lib import logger
from lib.models.motor import Motor, MotorKinds
from lib.repositories.repo import Repository, RepositoryNotInitializedException


class MotorRepository(Repository):
    """
    Enables database CRUD operations with models.Motor

    Init Attributes:
        motor: models.Motor
    """

    def __init__(self, motor: Motor = None):
        super().__init__("motors")
        self._motor = motor
        self._motor_id = None

    @property
    def motor(self) -> Motor:
        return self._motor

    @motor.setter
    def motor(self, motor: "Motor"):
        self._motor = motor

    @property
    def motor_id(self) -> str:
        return str(self._motor_id)

    @motor_id.setter
    def motor_id(self, motor_id: "str"):
        self._motor_id = motor_id

    async def insert_motor(self, motor_data: dict):
        collection = self.get_collection()
        result = await collection.insert_one(motor_data)
        self.motor_id = result.inserted_id
        return self

    async def update_motor(self, motor_data: dict, motor_id: str):
        collection = self.get_collection()
        await collection.update_one(
            {"_id": ObjectId(motor_id)}, {"$set": motor_data}
        )
        return self

    async def find_motor(self, motor_id: str):
        collection = self.get_collection()
        return await collection.find_one({"_id": ObjectId(motor_id)})

    async def delete_motor(self, motor_id: str):
        collection = self.get_collection()
        await collection.delete_one({"motor_id": motor_id})
        return self

    async def create_motor(self):
        """
        Creates a models.Motor in the database

        Returns:
            self
        """
        try:
            motor_to_dict = self.motor.dict()
            motor_to_dict["motor_kind"] = self.motor.motor_kind.value
            await self.insert_motor(motor_to_dict)
        except PyMongoError as e:
            raise e from e
        except RepositoryNotInitializedException as e:
            raise e from e
        else:
            return self
        finally:
            logger.info(
                f"Call to repositories.motor.create_motor completed for Motor {self.motor_id}"
            )

    async def get_motor_by_id(self, motor_id: str) -> Union[motor, None]:
        """
        Gets a models.Motor from the database

        Returns:
            self
        """
        try:
            read_motor = await self.find_motor(motor_id)
            parsed_motor = Motor.parse_obj(read_motor) if read_motor else None
            parsed_motor.set_motor_kind(MotorKinds(read_motor["motor_kind"]))
            self.motor = parsed_motor
        except PyMongoError as e:
            raise e from e
        except RepositoryNotInitializedException as e:
            raise e from e
        else:
            return self
        finally:
            logger.info(
                f"Call to repositories.motor.get_motor completed for Motor {motor_id}"
            )

    async def delete_motor_by_id(self, motor_id: str):
        """
        Deletes a models.Motor from the database

        Returns:
            self
        """
        try:
            await self.delete_motor(motor_id)
        except PyMongoError as e:
            raise e from e
        except RepositoryNotInitializedException as e:
            raise e from e
        else:
            return self
        finally:
            logger.info(
                f"Call to repositories.motor.delete_motor completed for Motor {motor_id}"
            )

    async def update_motor_by_id(self, motor_id: str):
        """
        Updates a models.Motor in the database

        Returns:
            self
        """
        try:
            motor_to_dict = self.motor.dict()
            motor_to_dict["motor_kind"] = self.motor.motor_kind.value
            await self.update_motor(motor_to_dict, motor_id)
        except PyMongoError as e:
            raise e from e
        except RepositoryNotInitializedException as e:
            raise e from e
        else:
            return self
        finally:
            logger.info(
                f"Call to repositories.motor.update_motor completed for Motor {motor_id}"
            )
