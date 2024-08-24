from typing import Union
from fastapi import HTTPException, status
from pymongo.errors import PyMongoError


import jsonpickle

from lib import logger, parse_error
from lib.models.environment import Env
from lib.models.rocket import Rocket
from lib.models.flight import Flight
from lib.views.flight import (
    FlightSummary,
    FlightCreated,
    FlightUpdated,
    FlightDeleted,
    FlightPickle,
)
from lib.repositories.flight import FlightRepository
from lib.services.flight import FlightService


class FlightController:
    """
    Controller for the Flight model.

    Init Attributes:
        flight (models.Flight): Flight model object.

    Enables:
        - Create a RocketPyFlight object from a Flight model object.
        - Generate trajectory simulation from a RocketPyFlight object.
        - Create both Flight model and RocketPyFlight objects in the database.
        - Update both Flight model and RocketPyFlight objects in the database.
        - Delete both Flight model and RocketPyFlight objects from the database.
        - Read a Flight model from the database.
        - Read a RocketPyFlight object from the database.

    """

    def __init__(
        self,
        flight: Flight,
    ):
        self._flight = flight

    @property
    def flight(self) -> Flight:
        return self._flight

    @flight.setter
    def flight(self, flight: Flight):
        self._flight = flight

    async def create_flight(self) -> Union[FlightCreated, HTTPException]:
        """
        Create a flight in the database.

        Returns:
            views.FlightCreated
        """
        try:
            async with FlightRepository(self.flight) as flight_repo:
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
                f"Call to controllers.flight.create_flight completed for Flight {flight_repo.flight_id}"
            )

    @staticmethod
    async def get_flight_by_id(flight_id: str) -> Union[Flight, HTTPException]:
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
                read_flight = flight_repo.flight
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
            if read_flight:
                return read_flight
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Flight not found.",
            )
        finally:
            logger.info(
                f"Call to controllers.flight.get_flight_by_id completed for Flight {flight_id}"
            )

    @classmethod
    async def get_rocketpy_flight_as_jsonpickle(
        cls,
        flight_id: str,
    ) -> Union[FlightPickle, HTTPException]:
        """
        Get rocketpy.flight as jsonpickle string.

        Args:
            flight_id: str

        Returns:
            views.FlightPickle

        Raises:
            HTTP 404 Not Found: If the flight is not found in the database.
        """
        try:
            read_flight = await cls.get_flight_by_id(flight_id)
            rocketpy_flight = FlightService.from_flight_model(read_flight)
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(
                f"controllers.flight.get_rocketpy_flight_as_jsonpickle: {exc_str}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read flight: {exc_str}",
            ) from e
        else:
            return FlightPickle(
                jsonpickle_rocketpy_flight=jsonpickle.encode(rocketpy_flight)
            )
        finally:
            logger.info(
                f"Call to controllers.flight.get_rocketpy_flight_as_jsonpickle completed for Flight {flight_id}"
            )

    async def update_flight_by_id(
        self, flight_id: str
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
            async with FlightRepository(self.flight) as flight_repo:
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
            read_flight = await cls.get_flight_by_id(flight_id)
            new_flight = read_flight.dict()
            new_flight["environment"] = env
            new_flight = Flight(**new_flight)
            async with FlightRepository(new_flight) as flight_repo:
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
            read_flight = await cls.get_flight_by_id(flight_id)
            updated_rocket = rocket.dict()
            updated_rocket["rocket_option"] = rocket.rocket_option.value
            updated_rocket["motor"][
                "motor_kind"
            ] = rocket.motor.motor_kind.value
            new_flight = read_flight.dict()
            new_flight["rocket"] = updated_rocket
            new_flight = Flight(**new_flight)
            async with FlightRepository(new_flight) as flight_repo:
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
            read_flight = await cls.get_flight_by_id(flight_id=flight_id)
            rocketpy_flight = FlightService.from_flight_model(read_flight)
            flight_summary = rocketpy_flight.get_flight_summary()
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
