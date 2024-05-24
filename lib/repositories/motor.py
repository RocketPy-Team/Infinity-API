from typing import Union
from lib import logging, parse_error
from lib.models.motor import Motor
from lib.repositories.repo import Repository

logger = logging.getLogger(__name__)


class MotorRepository(Repository):
    """
    Enables database CRUD operations with models.Motor

    Init Attributes:
        motor: models.Motor
        motor_id: str

    """

    def __init__(self):
        super().__init__("motors")
        self._motor = None
        self._motor_id = None

    def fetch_motor(self, motor: Motor):
        self.motor = motor
        self.motor_id = motor.motor_id
        return self

    @property
    def motor(self) -> Motor:
        return self._motor

    @motor.setter
    def motor(self, motor: "Motor"):
        self._motor = motor

    @property
    def motor_id(self) -> str:
        return self._motor_id

    @motor_id.setter
    def motor_id(self, motor_id: "str"):
        self._motor_id = motor_id

    async def insert_motor(self, motor_data: dict):
        await self.collection.insert_one(motor_data)
        return self

    async def find_motor(self, motor_id: str):
        return await self.collection.find_one({"motor_id": motor_id})

    async def delete_motor(self, motor_id: str):
        await self.collection.delete_one({"motor_id": motor_id})
        return self

    async def create_motor(self, motor_kind: str = "SOLID"):
        """
        Creates a non-existing models.Motor in the database

        Args:
            motor_kind: models.motor.MotorKinds

        Returns:
            self
        """
        try:
            motor_to_dict = self.motor.dict()
            motor_to_dict["motor_id"] = self.motor_id
            motor_to_dict["motor_kind"] = motor_kind
            await self.insert_motor(motor_to_dict)
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"repositories.motor.create_motor: {exc_str}")
            raise Exception(f"Error creating motor: {exc_str}") from e
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
            self.motor = parsed_motor
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"repositories.motor.get_motor: {exc_str}")
            raise Exception(f"Error getting motor: {exc_str}") from e
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
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"repositories.motor.delete_motor: {exc_str}")
            raise Exception(f"Error deleting motor: {exc_str}") from e
        else:
            return self
        finally:
            logger.info(
                f"Call to repositories.motor.delete_motor completed for Motor {motor_id}"
            )
