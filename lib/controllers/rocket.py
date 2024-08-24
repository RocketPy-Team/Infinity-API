from typing import Union
import jsonpickle

from fastapi import HTTPException, status
from pymongo.errors import PyMongoError

# TODO
# from inspect import getsourcelines

from lib import logger, parse_error
from lib.services.rocket import RocketService
from lib.models.rocket import Rocket
from lib.repositories.rocket import RocketRepository
from lib.views.rocket import (
    RocketSummary,
    RocketCreated,
    RocketUpdated,
    RocketDeleted,
    RocketPickle,
)


class RocketController:
    """
    Controller for the Rocket model.

    Init Attributes:
        rocket: models.Rocket.

    Enables:
       - CRUD operations over models.Rocket on the database.
    """

    def __init__(
        self,
        rocket: Rocket,
    ):
        self._rocket = rocket

    @property
    def rocket(self) -> Rocket:
        return self._rocket

    @rocket.setter
    def rocket(self, rocket: Rocket):
        self._rocket = rocket

    async def create_rocket(self) -> Union[RocketCreated, HTTPException]:
        """
        Create a models.Rocket in the database.

        Returns:
            views.RocketCreated
        """
        try:
            async with RocketRepository(self.rocket) as rocket_repo:
                await rocket_repo.create_rocket()
        except PyMongoError as e:
            logger.error(f"controllers.rocket.create_rocket: PyMongoError {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to create rocket in the db",
            ) from e
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.rocket.create_rocket: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create rocket: {exc_str}",
            ) from e
        else:
            return RocketCreated(rocket_id=rocket_repo.rocket_id)
        finally:
            logger.info(
                f"Call to controllers.rocket.create_rocket completed for Rocket {rocket_repo.rocket_id}"
            )

    @staticmethod
    async def get_rocket_by_id(
        rocket_id: str,
    ) -> Union[Rocket, HTTPException]:
        """
        Get a rocket from the database.

        Args:
            rocket_id: str

        Returns:
            models.Rocket

        Raises:
            HTTP 404 Not Found: If the rocket is not found in the database.
        """
        try:
            async with RocketRepository() as rocket_repo:
                await rocket_repo.get_rocket_by_id(rocket_id)
                read_rocket = rocket_repo.rocket
        except PyMongoError as e:
            logger.error(
                f"controllers.rocket.get_rocket_by_id: PyMongoError {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to read rocket from db",
            ) from e
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.rocket.get_rocket_by_id: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read rocket: {exc_str}",
            ) from e
        else:
            if read_rocket:
                return read_rocket
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rocket not found",
            )
        finally:
            logger.info(
                f"Call to controllers.rocket.get_rocket_by_id completed for Rocket {rocket_id}"
            )

    @classmethod
    async def get_rocketpy_rocket_as_jsonpickle(
        cls, rocket_id: str
    ) -> Union[RocketPickle, HTTPException]:
        """
        Get a rocketpy.Rocket object as jsonpickle string.

        Args:
            rocket_id: str

        Returns:
            views.RocketPickle

        Raises:
            HTTP 404 Not Found: If the rocket is not found in the database.
        """
        try:
            read_rocket = await cls.get_rocket_by_id(rocket_id)
            rocketpy_rocket = RocketService.from_rocket_model(read_rocket)
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(
                f"controllers.rocket.get_rocketpy_rocket_as_jsonpickle: {exc_str}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read rocket: {exc_str}",
            ) from e
        else:
            return RocketPickle(
                jsonpickle_rocketpy_rocket=jsonpickle.encode(rocketpy_rocket)
            )
        finally:
            logger.info(
                f"Call to controllers.rocket.get_rocketpy_rocket_as_jsonpickle completed for Rocket {rocket_id}"
            )

    async def update_rocket_by_id(
        self, rocket_id: str
    ) -> Union[RocketUpdated, HTTPException]:
        """
        Update a models.Rocket in the database.

        Args:
            rocket_id: str

        Returns:
            views.RocketUpdated

        Raises:
            HTTP 404 Not Found: If the rocket is not found in the database.
        """
        try:
            async with RocketRepository(self.rocket) as rocket_repo:
                await rocket_repo.update_rocket_by_id(rocket_id)
        except PyMongoError as e:
            logger.error(f"controllers.rocket.update_rocket: PyMongoError {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to update rocket in the db",
            ) from e
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.rocket.update_rocket: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update rocket: {exc_str}",
            ) from e
        else:
            return RocketUpdated(rocket_id=rocket_id)
        finally:
            logger.info(
                f"Call to controllers.rocket.update_rocket completed for Rocket {rocket_id}"
            )

    @staticmethod
    async def delete_rocket_by_id(
        rocket_id: str,
    ) -> Union[RocketDeleted, HTTPException]:
        """
        Delete a models.Rocket from the database.

        Args:
            rocket_id: str

        Returns:
            views.RocketDeleted

        Raises:
            HTTP 404 Not Found: If the rocket is not found in the database.
        """
        try:
            async with RocketRepository() as rocket_repo:
                await rocket_repo.delete_rocket_by_id(rocket_id)
        except PyMongoError as e:
            logger.error(f"controllers.rocket.delete_rocket: PyMongoError {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to delete rocket from db",
            ) from e
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.rocket.delete_rocket: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete rocket: {exc_str}",
            ) from e
        else:
            return RocketDeleted(rocket_id=rocket_id)
        finally:
            logger.info(
                f"Call to controllers.rocket.delete_rocket completed for Rocket {rocket_id}"
            )

    @classmethod
    async def simulate_rocket(
        cls,
        rocket_id: str,
    ) -> Union[RocketSummary, HTTPException]:
        """
        Simulate a rocketpy rocket.

        Args:
            rocket_id: str

        Returns:
            views.RocketSummary

        Raises:
            HTTP 404 Not Found: If the rocket does not exist in the database.
        """
        try:
            read_rocket = await cls.get_rocket_by_id(rocket_id)
            rocketpy_rocket = RocketService.from_rocket_model(read_rocket)
            rocket_summary = rocketpy_rocket.get_rocket_summary()
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.rocket.simulate: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to simulate rocket: {exc_str}",
            ) from e
        else:
            return rocket_summary
        finally:
            logger.info(
                f"Call to controllers.rocket.simulate completed for Rocket {rocket_id}"
            )
