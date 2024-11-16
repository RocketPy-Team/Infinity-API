from typing import Union
from fastapi import HTTPException, status
from pymongo.errors import PyMongoError

from lib import logger, parse_error
from lib.models.motor import Motor, MotorKinds
from lib.services.motor import MotorService
from lib.repositories.motor import MotorRepository
from lib.views.motor import (
    MotorSummary,
    MotorCreated,
    MotorUpdated,
    MotorDeleted,
    MotorView,
)


class MotorController:
    """
    Controller for the motor model.

    Enables:
        - Create a rocketpy.Motor object from a Motor model object.
    """

    @staticmethod
    def guard(motor: Motor):
        if (
            motor.motor_kind not in (MotorKinds.SOLID, MotorKinds.GENERIC)
            and motor.tanks is None
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Tanks must be provided for liquid and hybrid motors.",
            )

        # TODO: extend guard to check motor kinds and tank kinds specifics

    @classmethod
    async def create_motor(
        cls, motor: Motor
    ) -> Union[MotorCreated, HTTPException]:
        """
        Create a models.Motor in the database.

        Returns:
            views.MotorCreated
        """
        motor_repo = None
        try:
            cls.guard(motor)
            async with MotorRepository(motor) as motor_repo:
                await motor_repo.create_motor()
        except PyMongoError as e:
            logger.error(f"controllers.motor.create_motor: PyMongoError {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to create motor in db",
            ) from e
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.motor.create_motor: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create motor: {exc_str}",
            ) from e
        else:
            return MotorCreated(motor_id=motor_repo.motor_id)
        finally:
            logger.info(
                f"Call to controllers.motor.create_motor completed for Motor {None or motor_repo.motor_id}"
            )

    @staticmethod
    async def get_motor_by_id(
        motor_id: str,
    ) -> Union[MotorView, HTTPException]:
        """
        Get a models.Motor from the database.

        Args:
            motor_id: str

        Returns:
            models.Motor

        Raises:
            HTTP 404 Not Found: If the motor is not found in the database.
        """
        try:
            async with MotorRepository() as motor_repo:
                await motor_repo.get_motor_by_id(motor_id)
                motor = motor_repo.motor
        except PyMongoError as e:
            logger.error(
                f"controllers.motor.get_motor_by_id: PyMongoError {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to read motor from db",
            ) from e
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.motor.get_motor_by_id: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read motor: {exc_str}",
            ) from e
        else:
            if motor:
                motor_view = MotorView(
                    **motor.dict(), selected_motor_kind=motor.motor_kind
                )
                return motor_view
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Motor not found",
            )
        finally:
            logger.info(
                f"Call to controllers.motor.get_motor_by_id completed for Motor {motor_id}"
            )

    @classmethod
    async def get_rocketpy_motor_binary(
        cls,
        motor_id: str,
    ) -> Union[bytes, HTTPException]:
        """
        Get a rocketpy.Motor object as a dill binary.

        Args:
            motor_id: str

        Returns:
            bytes

        Raises:
            HTTP 404 Not Found: If the motor is not found in the database.
        """
        try:
            motor = await cls.get_motor_by_id(motor_id)
            motor_service = MotorService.from_motor_model(motor)
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(
                f"controllers.motor.get_rocketpy_motor_binary: {exc_str}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read motor: {exc_str}",
            ) from e
        else:
            return motor_service.get_motor_binary()
        finally:
            logger.info(
                f"Call to controllers.motor.get_rocketpy_motor_binary completed for Motor {motor_id}"
            )

    @classmethod
    async def update_motor_by_id(
        cls, motor_id: str, motor: Motor
    ) -> Union[MotorUpdated, HTTPException]:
        """
        Update a motor in the database.

        Args:
            motor_id: str

        Returns:
            views.MotorUpdated

        Raises:
            HTTP 404 Not Found: If the motor is not found in the database.
        """
        try:
            cls.guard(motor)
            async with MotorRepository(motor) as motor_repo:
                await motor_repo.update_motor_by_id(motor_id)
        except PyMongoError as e:
            logger.error(f"controllers.motor.update_motor: PyMongoError {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to update motor in db",
            ) from e
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.motor.update_motor: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update motor: {exc_str}",
            ) from e
        else:
            return MotorUpdated(motor_id=motor_id)
        finally:
            logger.info(
                f"Call to controllers.motor.update_motor completed for Motor {motor_id}"
            )

    @staticmethod
    async def delete_motor_by_id(
        motor_id: str,
    ) -> Union[MotorDeleted, HTTPException]:
        """
        Delete a models.Motor from the database.

        Args:
            motor_id: str

        Returns:
            views.MotorDeleted

        Raises:
            HTTP 404 Not Found: If the motor is not found in the database.
        """
        try:
            async with MotorRepository() as motor_repo:
                await motor_repo.delete_motor_by_id(motor_id)
        except PyMongoError as e:
            logger.error(f"controllers.motor.delete_motor: PyMongoError {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to delete motor from db",
            ) from e
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.motor.delete_motor: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete motor: {exc_str}",
            ) from e
        else:
            return MotorDeleted(motor_id=motor_id)
        finally:
            logger.info(
                f"Call to controllers.motor.delete_motor completed for Motor {motor_id}"
            )

    @classmethod
    async def simulate_motor(
        cls, motor_id: str
    ) -> Union[MotorSummary, HTTPException]:
        """
        Simulate a rocketpy motor.

        Args:
            motor_id: str

        Returns:
            views.MotorSummary

        Raises:
            HTTP 404 Not Found: If the motor does not exist in the database.
        """
        try:
            motor = await cls.get_motor_by_id(motor_id)
            motor_service = MotorService.from_motor_model(motor)
            motor_summary = motor_service.get_motor_summary()
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.motor.simulate_motor: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to simulate motor: {exc_str}",
            ) from e
        else:
            return motor_summary
        finally:
            logger.info(
                f"Call to controllers.motor.simulate_motor completed for Motor {motor_id}"
            )
