from typing import Union
from lib import logging, parse_error
from lib.models.rocket import Rocket
from lib.repositories.repo import Repository

logger = logging.getLogger(__name__)


class RocketRepository(Repository):
    """
    Enables database CRUD operations with models.Rocket

    Init Attributes:
        rocket: models.Rocket
        rocket_id: str

    """

    def __init__(self, rocket: Rocket = None, rocket_id: str = None):
        super().__init__("rockets")
        self._rocket = rocket
        if rocket_id:
            self._rocket_id = rocket_id
        else:
            self._rocket_id = str(hash(self._rocket))

    def __del__(self):
        self.connection.close()
        super().__del__()

    @property
    def rocket(self) -> Rocket:
        return self._rocket

    @rocket.setter
    def rocket(self, rocket: "Rocket"):
        self._rocket = rocket

    @property
    def rocket_id(self) -> str:
        return self._rocket_id

    @rocket_id.setter
    def rocket_id(self, rocket_id: "str"):
        self._rocket_id = rocket_id

    async def create_rocket(
        self, rocket_option: str = "Calisto", motor_kind: str = "Solid"
    ):
        """
        Creates a non-existing models.Rocket in the database

        Args:
            rocket_option: models.rocket.RocketOptions
            motor_kind: models.motor.MotorKinds

        Returns:
            self
        """
        try:
            rocket_to_dict = self.rocket.dict()
            rocket_to_dict["rocket_id"] = self.rocket_id
            rocket_to_dict["rocket_option"] = rocket_option
            rocket_to_dict["motor"]["motor_kind"] = motor_kind
            await self.collection.insert_one(rocket_to_dict)
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"repositories.rocket.create_rocket: {exc_str}")
            raise Exception(f"Error creating rocket: {str(e)}") from e
        else:
            return self
        finally:
            logger.info(
                f"Call to repositories.rocket.create_rocket completed for Rocket {self.rocket_id}"
            )

    async def update_rocket(self, rocket_option: str = "Calisto", motor_kind: str = "Solid"):
        """
        Updates a models.Rocket in the database

        Returns:
            self
        """
        try:
            rocket_to_dict = self.rocket.dict()
            rocket_to_dict["rocket_id"] = str(hash(self.rocket))
            rocket_to_dict["rocket_option"] = rocket_option
            rocket_to_dict["motor"]["motor_kind"] = motor_kind
            await self.collection.update_one(
                {"rocket_id": self.rocket_id}, {"$set": rocket_to_dict}
            )

            self.rocket_id = rocket_to_dict["rocket_id"]
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"repositories.rocket.update_rocket: {exc_str}")
            raise Exception(f"Error updating rocket: {str(e)}") from e
        else:
            return self
        finally:
            logger.info(
                f"Call to repositories.rocket.update_rocket completed for Rocket {self.rocket_id}"
            )

    async def get_rocket(self) -> Union[Rocket, None]:
        """
        Gets a models.Rocket from the database

        Returns:
            models.Rocket
        """
        try:
            read_rocket = await self.collection.find_one(
                {"rocket_id": self.rocket_id}
            )
            parsed_rocket = (
                Rocket.parse_obj(read_rocket) if read_rocket else None
            )
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"repositories.rocket.get_rocket: {exc_str}")
            raise Exception(f"Error getting rocket: {str(e)}") from e
        else:
            return parsed_rocket
        finally:
            logger.info(
                f"Call to repositories.rocket.get_rocket completed for Rocket {self.rocket_id}"
            )

    async def delete_rocket(self):
        """
        Deletes a models.Rocket from the database

        Returns:
            None
        """
        try:
            await self.collection.delete_one({"rocket_id": self.rocket_id})
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"repositories.rocket.delete_rocket: {exc_str}")
            raise Exception(f"Error deleting rocket: {str(e)}") from e
        finally:
            logger.info(
                f"Call to repositories.rocket.delete_rocket completed for Rocket {self.rocket_id}"
            )
