from typing import Union

from fastapi import HTTPException, status
from pymongo.errors import PyMongoError

from lib import logger, parse_error
from lib.services.rocket import RocketService
from lib.models.rocket import Rocket
from lib.controllers.motor import MotorController
from lib.repositories.rocket import RocketRepository
from lib.views.motor import MotorView
from lib.views.rocket import (
    RocketSummary,
    RocketCreated,
    RocketUpdated,
    RocketDeleted,
    RocketView,
)


class RocketController:
    """
    Controller for the Rocket model.

    Enables:
       - CRUD operations over models.Rocket on the database.
    """

    @staticmethod
    def guard(rocket: Rocket):
        MotorController.guard(rocket.motor)

    @classmethod
    async def create_rocket(
        cls, rocket: Rocket
    ) -> Union[RocketCreated, HTTPException]:
        """
        Create a models.Rocket in the database.

        Returns:
            views.RocketCreated
        """
        try:
            cls.guard(rocket)
            async with RocketRepository(rocket) as rocket_repo:
                await rocket_repo.create_rocket()
        except PyMongoError as e:
            logger.error(f"controllers.rocket.create_rocket: PyMongoError {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to create rocket in the db",
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
    ) -> Union[RocketView, HTTPException]:
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
                rocket = rocket_repo.rocket
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
            if rocket:
                motor_view = MotorView(
                    **rocket.motor.dict(),
                    selected_motor_kind=rocket.motor.motor_kind,
                )
                updated_rocket = rocket.dict()
                updated_rocket.update(motor=motor_view)
                rocket_view = RocketView(
                    **updated_rocket,
                )
                return rocket_view
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rocket not found",
            )
        finally:
            logger.info(
                f"Call to controllers.rocket.get_rocket_by_id completed for Rocket {rocket_id}"
            )

    @classmethod
    async def get_rocketpy_rocket_binary(
        cls, rocket_id: str
    ) -> Union[bytes, HTTPException]:
        """
        Get a rocketpy.Rocket object as dill binary.

        Args:
            rocket_id: str

        Returns:
            bytes

        Raises:
            HTTP 404 Not Found: If the rocket is not found in the database.
        """
        try:
            rocket = await cls.get_rocket_by_id(rocket_id)
            rocket_service = RocketService.from_rocket_model(rocket)
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(
                f"controllers.rocket.get_rocketpy_rocket_binary: {exc_str}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read rocket: {exc_str}",
            ) from e
        else:
            return rocket_service.get_rocket_binary()
        finally:
            logger.info(
                f"Call to controllers.rocket.get_rocketpy_rocket_binary completed for Rocket {rocket_id}"
            )

    @classmethod
    async def update_rocket_by_id(
        cls, rocket: Rocket, rocket_id: str
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
            cls.guard(rocket)
            async with RocketRepository(rocket) as rocket_repo:
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
            rocket = await cls.get_rocket_by_id(rocket_id)
            rocket_service = RocketService.from_rocket_model(rocket)
            rocket_summary = rocket_service.get_rocket_summary()
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
