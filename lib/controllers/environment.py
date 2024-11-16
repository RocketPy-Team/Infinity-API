from typing import Union

from fastapi import HTTPException, status
from pymongo.errors import PyMongoError

from lib import logger, parse_error
from lib.models.environment import Env
from lib.services.environment import EnvironmentService
from lib.repositories.environment import EnvRepository
from lib.views.environment import (
    EnvSummary,
    EnvCreated,
    EnvDeleted,
    EnvUpdated,
)


class EnvController:
    """
    Controller for the Environment model.

    Enables:
        - Simulation of a RocketPy Environment from models.Env
        - CRUD operations over models.Env on the database
    """

    @staticmethod
    async def create_env(env: Env) -> Union[EnvCreated, HTTPException]:
        """
        Create a env in the database.

        Returns:
            views.EnvCreated
        """
        env_repo = None
        try:
            async with EnvRepository(env) as env_repo:
                await env_repo.create_env()
        except PyMongoError as e:
            logger.error(
                f"controllers.environment.create_env: PyMongoError {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to create environment in db",
            ) from e
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.environment.create_env: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create environment: {exc_str}",
            ) from e
        else:
            return EnvCreated(env_id=env_repo.env_id)
        finally:
            logger.info(
                f"Call to controllers.environment.create_env completed for Env {None or env_repo.env_id}"
            )

    @staticmethod
    async def get_env_by_id(env_id: str) -> Union[Env, HTTPException]:
        """
        Get a env from the database.

        Args:
            env_id: str

        Returns:
            models.Env

        Raises:
            HTTP 404 Not Found: If the env is not found in the database.
        """
        try:
            async with EnvRepository() as env_repo:
                await env_repo.get_env_by_id(env_id)
                env = env_repo.env
        except PyMongoError as e:
            logger.error(
                f"controllers.environment.get_env_by_id: PyMongoError {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to read environment from db",
            ) from e
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.environment.get_env_by_id: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read environment: {exc_str}",
            ) from e
        else:
            if env:
                return env
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Environment not found",
            )
        finally:
            logger.info(
                f"Call to controllers.environment.get_env_by_id completed for Env {env_id}"
            )

    @classmethod
    async def get_rocketpy_env_binary(
        cls,
        env_id: str,
    ) -> Union[bytes, HTTPException]:
        """
        Get rocketpy.Environmnet dill binary.

        Args:
            env_id: str

        Returns:
            bytes

        Raises:
            HTTP 404 Not Found: If the env is not found in the database.
        """
        try:
            env = await cls.get_env_by_id(env_id)
            env_service = EnvironmentService.from_env_model(env)
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(
                f"controllers.environment.get_rocketpy_env_as_binary: {exc_str}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read environment: {exc_str}",
            ) from e
        else:
            return env_service.get_env_binary()
        finally:
            logger.info(
                f"Call to controllers.environment.get_rocketpy_env_binary completed for Env {env_id}"
            )

    @staticmethod
    async def update_env_by_id(
        env_id: str, env: Env
    ) -> Union[EnvUpdated, HTTPException]:
        """
        Update a models.Env in the database.

        Args:
            env_id: str

        Returns:
            views.EnvUpdated

        Raises:
            HTTP 404 Not Found: If the env is not found in the database.
        """
        try:
            async with EnvRepository(env) as env_repo:
                await env_repo.update_env_by_id(env_id)
        except PyMongoError as e:
            logger.error(
                f"controllers.environment.update_env: PyMongoError {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to update environment from db",
            ) from e
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.environment.update_env: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update environment: {exc_str}",
            ) from e
        else:
            return EnvUpdated(env_id=env_id)
        finally:
            logger.info(
                f"Call to controllers.environment.update_env completed for Env {env_id}"
            )

    @staticmethod
    async def delete_env_by_id(
        env_id: str,
    ) -> Union[EnvDeleted, HTTPException]:
        """
        Delete a models.Env from the database.

        Args:
            env_id: str

        Returns:
            views.EnvDeleted

        Raises:
            HTTP 404 Not Found: If the env is not found in the database.
        """
        try:
            async with EnvRepository() as env_repo:
                await env_repo.delete_env_by_id(env_id)
        except PyMongoError as e:
            logger.error(
                f"controllers.environment.delete_env: PyMongoError {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to delete environment from db",
            ) from e
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.environment.delete_env: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete environment: {exc_str}",
            ) from e
        else:
            return EnvDeleted(env_id=env_id)
        finally:
            logger.info(
                f"Call to controllers.environment.delete_env completed for Env {env_id}"
            )

    @classmethod
    async def simulate_env(
        cls, env_id: str
    ) -> Union[EnvSummary, HTTPException]:
        """
        Simulate a rocket environment.

        Args:
            env_id: str.

        Returns:
            EnvSummary

        Raises:
            HTTP 404 Not Found: If the env does not exist in the database.
        """
        try:
            env = await cls.get_env_by_id(env_id)
            env_service = EnvironmentService.from_env_model(env)
            env_summary = env_service.get_env_summary()
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.environment.simulate: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to simulate environment: {exc_str}",
            ) from e
        else:
            return env_summary
        finally:
            logger.info(
                f"Call to controllers.environment.simulate completed for Env {env_id}"
            )
