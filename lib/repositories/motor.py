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

    def __init__(self, motor: Motor = None, motor_id: str = None) -> None:
        super().__init__("motors")
        self._motor = motor
        if motor_id:
            self._motor_id = motor_id
        else:
            self._motor_id = str(hash(self._motor))

    def __del__(self):
        self.connection.close()
        super().__del__()

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

    async def create_motor(self, motor_kind: str = "solid"):
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
            await self.collection.insert_one(motor_to_dict)
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"repositories.motor.create_motor: {exc_str}")
            raise Exception(f"Error creating motor: {str(e)}") from e
        else:
            return self
        finally:
            logger.info(
                f"Call to repositories.motor.create_motor completed for Motor {self.motor_id}"
            )

    async def update_motor(self, motor_kind: str = "solid"):
        """
        Updates a models.Motor in the database

        Returns:
            self
        """
        try:
            motor_to_dict = self.motor.dict()
            motor_to_dict["motor_id"] = str(hash(self.motor))
            motor_to_dict["motor_kind"] = motor_kind
            await self.collection.update_one(
                {"motor_id": self.motor_id}, {"$set": motor_to_dict}
            )
            self.motor_id = motor_to_dict["motor_id"]
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"repositories.motor.update_motor: {exc_str}")
            raise Exception(f"Error updating motor: {str(e)}") from e
        else:
            return self
        finally:
            logger.info(
                f"Call to repositories.motor.update_motor completed for Motor {self.motor_id}"
            )

    async def get_motor(self) -> Union[motor, None]:
        """
        Gets a models.Motor from the database

        Returns:
            models.Motor
        """
        try:
            read_motor = await self.collection.find_one(
                {"motor_id": self.motor_id}
            )
            parsed_motor = Motor.parse_obj(read_motor) if read_motor else None
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"repositories.motor.get_motor: {exc_str}")
            raise Exception(f"Error getting motor: {str(e)}") from e
        else:
            return parsed_motor
        finally:
            logger.info(
                f"Call to repositories.motor.get_motor completed for Motor {self.motor_id}"
            )

    async def delete_motor(self):
        """
        Deletes a models.Motor from the database

        Returns:
            None
        """
        try:
            await self.collection.delete_one({"motor_id": self.motor_id})
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"repositories.motor.delete_motor: {exc_str}")
            raise Exception(f"Error deleting motor: {str(e)}") from e
        finally:
            logger.info(
                f"Call to repositories.motor.delete_motor completed for Motor {self.motor_id}"
            )
