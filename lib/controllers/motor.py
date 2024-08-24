from typing import Union
from fastapi import HTTPException, status
from pymongo.errors import PyMongoError
import jsonpickle

from lib import logger, parse_error
from lib.models.motor import Motor, MotorKinds
from lib.services.motor import MotorService
from lib.repositories.motor import MotorRepository
from lib.views.motor import (
    MotorSummary,
    MotorCreated,
    MotorUpdated,
    MotorDeleted,
    MotorPickle,
)


class MotorController:
    """
    Controller for the motor model.

    Init Attributes:
        motor (models.Motor): Motor model object.

    Enables:
        - Create a rocketpy.Motor object from a Motor model object.
    """

    def __init__(self, motor: Motor):
        self.guard(motor)
        self._motor = motor

    @property
    def motor(self) -> Motor:
        return self._motor

    @motor.setter
    def motor(self, motor: Motor):
        self._motor = motor

    def guard(self, motor: Motor):
        if motor.motor_kind != MotorKinds.SOLID and motor.tanks is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Tanks must be provided for liquid and hybrid motors.",
            )

    async def create_motor(self) -> Union[MotorCreated, HTTPException]:
        """
        Create a models.Motor in the database.

        Returns:
            views.MotorCreated
        """
        try:
            async with MotorRepository(self.motor) as motor_repo:
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
                f"Call to controllers.motor.create_motor completed for Motor {motor_repo.motor_id}"
            )

    @staticmethod
    async def get_motor_by_id(motor_id: str) -> Union[Motor, HTTPException]:
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
                read_motor = motor_repo.motor
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
            if read_motor:
                return read_motor
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Motor not found",
            )
        finally:
            logger.info(
                f"Call to controllers.motor.get_motor_by_id completed for Motor {motor_id}"
            )

    @classmethod
    async def get_rocketpy_motor_as_jsonpickle(
        cls,
        motor_id: str,
    ) -> Union[MotorPickle, HTTPException]:
        """
        Get a rocketpy.Motor object as a jsonpickle string.

        Args:
            motor_id: str

        Returns:
            views.MotorPickle

        Raises:
            HTTP 404 Not Found: If the motor is not found in the database.
        """
        try:
            read_motor = await cls.get_motor_by_id(motor_id)
            rocketpy_motor = MotorService.from_motor_model(read_motor)
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(
                f"controllers.motor.get_rocketpy_motor_as_jsonpickle: {exc_str}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read motor: {exc_str}",
            ) from e
        else:
            return MotorPickle(
                jsonpickle_rocketpy_motor=jsonpickle.encode(rocketpy_motor)
            )
        finally:
            logger.info(
                f"Call to controllers.motor.get_rocketpy_motor_as_jsonpickle completed for Motor {motor_id}"
            )

    async def update_motor_by_id(
        self, motor_id: str
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
            async with MotorRepository(self.motor) as motor_repo:
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
            read_motor = await cls.get_motor_by_id(motor_id)
            rocketpy_motor = MotorService.from_motor_model(read_motor)
            motor_summary = rocketpy_motor.get_motor_summary()
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
