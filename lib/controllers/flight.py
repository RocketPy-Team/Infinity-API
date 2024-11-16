from typing import Union
from fastapi import HTTPException, status
from pymongo.errors import PyMongoError


from lib import logger, parse_error
from lib.controllers.rocket import RocketController
from lib.models.environment import Env
from lib.models.rocket import Rocket
from lib.models.flight import Flight
from lib.views.motor import MotorView
from lib.views.rocket import RocketView
from lib.views.flight import (
    FlightSummary,
    FlightCreated,
    FlightUpdated,
    FlightDeleted,
    FlightView,
)
from lib.repositories.flight import FlightRepository
from lib.services.flight import FlightService


class FlightController:
    """
    Controller for the Flight model.

    Enables:
        - Create a RocketPyFlight object from a Flight model object.
        - Generate trajectory simulation from a RocketPyFlight object.
        - Create both Flight model and RocketPyFlight objects in the database.
        - Update both Flight model and RocketPyFlight objects in the database.
        - Delete both Flight model and RocketPyFlight objects from the database.
        - Read a Flight model from the database.
        - Read a RocketPyFlight object from the database.

    """

    @staticmethod
    def guard(flight: Flight):
        RocketController.guard(flight.rocket)

    @classmethod
    async def create_flight(
        cls, flight: Flight
    ) -> Union[FlightCreated, HTTPException]:
        """
        Create a flight in the database.

        Returns:
            views.FlightCreated
        """
        flight_repo = None
        try:
            cls.guard(flight)
            async with FlightRepository(flight) as flight_repo:
                await flight_repo.create_flight()
        except PyMongoError as e:
            logger.error(f"controllers.flight.create_flight: PyMongoError {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to create flight in db",
            ) from e
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.flight.create_flight: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create flight: {exc_str}",
            ) from e
        else:
            return FlightCreated(flight_id=flight_repo.flight_id)
        finally:
            logger.info(
                f"Call to controllers.flight.create_flight completed for Flight {None or flight_repo.flight_id}"
            )

    @staticmethod
    async def get_flight_by_id(
        flight_id: str,
    ) -> Union[FlightView, HTTPException]:
        """
        Get a flight from the database.

        Args:
            flight_id: str

        Returns:
            models.Flight

        Raises:
            HTTP 404 Not Found: If the flight is not found in the database.
        """
        try:
            async with FlightRepository() as flight_repo:
                await flight_repo.get_flight_by_id(flight_id)
                flight = flight_repo.flight
        except PyMongoError as e:
            logger.error(
                f"controllers.flight.get_flight_by_id: PyMongoError {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to read flight from db",
            ) from e
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.flight.get_flight_by_id: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read flight: {exc_str}",
            ) from e
        else:
            if flight:
                motor_view = MotorView(
                    **flight.rocket.motor.dict(),
                    selected_motor_kind=flight.rocket.motor.motor_kind,
                )
                updated_rocket = flight.rocket.dict()
                updated_rocket.update(motor=motor_view)
                rocket_view = RocketView(
                    **updated_rocket,
                )
                updated_flight = flight.dict()
                updated_flight.update(rocket=rocket_view)
                flight_view = FlightView(**updated_flight)
                return flight_view
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Flight not found.",
            )
        finally:
            logger.info(
                f"Call to controllers.flight.get_flight_by_id completed for Flight {flight_id}"
            )

    @classmethod
    async def get_rocketpy_flight_binary(
        cls,
        flight_id: str,
    ) -> Union[bytes, HTTPException]:
        """
        Get rocketpy.flight as dill binary.

        Args:
            flight_id: str

        Returns:
            bytes

        Raises:
            HTTP 404 Not Found: If the flight is not found in the database.
        """
        try:
            flight = await cls.get_flight_by_id(flight_id)
            flight_service = FlightService.from_flight_model(flight)
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(
                f"controllers.flight.get_rocketpy_flight_binary: {exc_str}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read flight: {exc_str}",
            ) from e
        else:
            return flight_service.get_flight_binary()
        finally:
            logger.info(
                f"Call to controllers.flight.get_rocketpy_flight_binary completed for Flight {flight_id}"
            )

    @classmethod
    async def update_flight_by_id(
        cls, flight: Flight, flight_id: str
    ) -> Union[FlightUpdated, HTTPException]:
        """
        Update a models.Flight in the database.

        Args:
            flight_id: str

        Returns:
            views.FlightUpdated

        Raises:
            HTTP 404 Not Found: If the flight is not found in the database.
        """
        try:
            cls.guard(flight)
            async with FlightRepository(flight) as flight_repo:
                await flight_repo.update_flight_by_id(flight_id)
        except PyMongoError as e:
            logger.error(f"controllers.flight.update_flight: PyMongoError {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to update flight in db",
            ) from e
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.flight.update_flight: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update flight: {exc_str}",
            ) from e
        else:
            return FlightUpdated(flight_id=flight_id)
        finally:
            logger.info(
                f"Call to controllers.flight.update_flight completed for Flight {flight_id}"
            )

    @classmethod
    async def update_env_by_flight_id(
        cls, flight_id: str, *, env: Env
    ) -> Union[FlightUpdated, HTTPException]:
        """
        Update a models.Flight.env in the database.

        Args:
            flight_id: str
            env: models.Env

        Returns:
            views.FlightUpdated

        Raises:
            HTTP 404 Not Found: If the flight is not found in the database.
        """
        try:
            flight = await cls.get_flight_by_id(flight_id)
            flight.environment = env
            async with FlightRepository(flight) as flight_repo:
                await flight_repo.update_env_by_flight_id(flight_id)
        except PyMongoError as e:
            logger.error(
                f"controllers.flight.update_env_by_flight_id: PyMongoError {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to update environment from db",
            ) from e
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.flight.update_env: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update environment: {exc_str}",
            ) from e
        else:
            return FlightUpdated(flight_id=flight_id)
        finally:
            logger.info(
                f"Call to controllers.flight.update_env completed for Flight {flight_id}"
            )

    @classmethod
    async def update_rocket_by_flight_id(
        cls, flight_id: str, *, rocket: Rocket
    ) -> Union[FlightUpdated, HTTPException]:
        """
        Update a models.Flight.rocket in the database.

        Args:
            flight_id: str
            rocket: models.Rocket

        Returns:
            views.FlightUpdated

        Raises:
            HTTP 404 Not Found: If the flight is not found in the database.
        """
        try:
            flight = await cls.get_flight_by_id(flight_id)
            flight.rocket = rocket
            async with FlightRepository(flight) as flight_repo:
                await flight_repo.update_rocket_by_flight_id(flight_id)
        except PyMongoError as e:
            logger.error(
                f"controllers.flight.update_rocket_by_flight_id: PyMongoError {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to update rocket from db",
            ) from e
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.flight.update_rocket: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update rocket: {exc_str}",
            ) from e
        else:
            return FlightUpdated(flight_id=flight_id)
        finally:
            logger.info(
                f"Call to controllers.flight.update_rocket completed for Flight {flight_id}"
            )

    @staticmethod
    async def delete_flight_by_id(
        flight_id: str,
    ) -> Union[FlightDeleted, HTTPException]:
        """
        Delete a models.Flight from the database.

        Args:
            flight_id: str

        Returns:
            views.FlightDeleted

        Raises:
            HTTP 404 Not Found: If the flight is not found in the database.
        """
        try:
            async with FlightRepository() as flight_repo:
                await flight_repo.delete_flight_by_id(flight_id)
        except PyMongoError as e:
            logger.error(f"controllers.flight.delete_flight: PyMongoError {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to delete flight from db",
            ) from e
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.flight.delete_flight: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete flight: {exc_str}",
            ) from e
        else:
            return FlightDeleted(flight_id=flight_id)
        finally:
            logger.info(
                f"Call to controllers.flight.delete_flight completed for Flight {flight_id}"
            )

    @classmethod
    async def simulate_flight(
        cls,
        flight_id: str,
    ) -> Union[FlightSummary, HTTPException]:
        """
        Simulate a rocket flight.

        Args:
            flight_id: str

        Returns:
            Flight summary view.

        Raises:
            HTTP 404 Not Found: If the flight does not exist in the database.
        """
        try:
            flight = await cls.get_flight_by_id(flight_id=flight_id)
            flight_service = FlightService.from_flight_model(flight)
            flight_summary = flight_service.get_flight_summary()
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.flight.simulate_flight: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to simulate flight: {exc_str}",
            ) from e
        else:
            return flight_summary
        finally:
            logger.info(
                f"Call to controllers.flight.simulate_flight completed for Flight {flight_id}"
            )
