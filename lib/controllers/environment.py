from typing import Union
from datetime import datetime

import logging
import jsonpickle
from rocketpy.environment.environment import Environment as RocketPyEnvironment
from fastapi import HTTPException, status

from lib.controllers import parse_error
from lib.models.environment import Env
from lib.repositories.environment import EnvRepository
from lib.views.environment import (
    EnvSummary,
    EnvData,
    EnvPlots,
    EnvCreated,
    EnvDeleted,
    EnvUpdated,
    EnvPickle,
)


class EnvController:
    """
    Controller for the Environment model.

    Init Attributes:
        env: models.Env

    Enables:
        - Simulation of RocketPyEnvironment from models.Env
        - CRUD operations over modeols.Env on the database
    """

    def __init__(self, env: Env):
        self._env = env

    @property
    def env(self) -> Env:
        return self._env

    @env.setter
    def env(self, env: Env):
        self._env = env

    @staticmethod
    async def get_rocketpy_env(env: Env) -> RocketPyEnvironment:
        """
        Get the rocketpy env object.

        Returns:
            RocketPyEnvironment
        """
        rocketpy_env = RocketPyEnvironment(
            latitude=env.latitude,
            longitude=env.longitude,
            elevation=env.elevation,
            date=env.date,
        )
        rocketpy_env.set_atmospheric_model(
            type=env.atmospheric_model_type, file=env.atmospheric_model_file
        )
        return rocketpy_env

    async def create_env(self) -> "Union[EnvCreated, HTTPException]":
        """
        Create a env in the database.

        Returns:
            views.EnvCreated
        """
        env_repo = EnvRepository(environment=self.env)
        try:
            await env_repo.create_env()
        except Exception as e:
            exc_str = parse_error(e)
            logging.error(
                f"[{datetime.now()}] controllers.environment.create_env: {exc_str}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create environment: {e}",
            ) from e
        else:
            return EnvCreated(env_id=env_repo.env_id)
        finally:
            logging.info(
                f"[{datetime.now()}] Call to controllers.environment.create_env completed; params: Env {hash(self.env)}"
            )

    @staticmethod
    async def get_env_by_id(env_id: int) -> "Union[Env, HTTPException]":
        """
        Get a env from the database.

        Args:
            env_id: int

        Returns:
            models.Env

        Raises:
            HTTP 404 Not Found: If the env is not found in the database.
        """
        env_repo = EnvRepository(env_id=env_id)
        try:
            read_env = await env_repo.get_env()
        except Exception as e:
            exc_str = parse_error(e)
            logging.error(
                f"[{datetime.now()}] controllers.environment.get_env_by_id: {exc_str}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read environment: {e}",
            ) from e
        else:
            if read_env:
                return read_env
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Environment not found",
            )
        finally:
            logging.info(
                f"[{datetime.now()}] Call to controllers.environment.get_env_by_id completed; params: EnvID {env_id}"
            )

    @classmethod
    async def get_rocketpy_env_as_jsonpickle(
        cls,
        env_id: int,
    ) -> "Union[EnvPickle, HTTPException]":
        """
        Get rocketpy.Environmnet as jsonpickle string.

        Args:
            env_id: int

        Returns:
            views.EnvPickle

        Raises:
            HTTP 404 Not Found: If the env is not found in the database.
        """
        env_repo = EnvRepository(env_id=env_id)
        try:
            read_env = await env_repo.get_env()
        except Exception as e:
            exc_str = parse_error(e)
            logging.error(
                f"[{datetime.now()}] controllers.environment.get_rocketpy_env_as_jsonpickle: {exc_str}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read environment: {e}",
            ) from e
        else:
            if read_env:
                rocketpy_env = cls.get_rocketpy_env(read_env)
                return EnvPickle(
                    jsonpickle_rocketpy_env=jsonpickle.encode(rocketpy_env)
                )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Environment not found",
            )
        finally:
            logging.info(
                f"[{datetime.now()}] Call to controllers.environment.get_rocketpy_env_as_jsonpickle completed; params: EnvID {env_id}"
            )

    async def update_env(
        self, env_id: int
    ) -> "Union[EnvUpdated, HTTPException]":
        """
        Update a env in the database.

        Args:
            env_id: int

        Returns:
            views.EnvUpdated

        Raises:
            HTTP 404 Not Found: If the env is not found in the database.
        """
        env_repo = EnvRepository(environment=self.env, env_id=env_id)
        try:
            read_env = await env_repo.get_env()
            if read_env:
                await env_repo.update_env()
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Environment not found",
                )
        except Exception as e:
            exc_str = parse_error(e)
            logging.error(
                f"[{datetime.now()}] controllers.environment.update_env: {exc_str}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update environment: {e}",
            ) from e
        else:
            return EnvUpdated(new_env_id=env_repo.env_id)
        finally:
            logging.info(
                f"[{datetime.now()}] Call to controllers.environment.update_env completed; params: EnvID {env_id}, Env {hash(self.env)}"
            )

    @staticmethod
    async def delete_env(env_id: str) -> "Union[EnvDeleted, HTTPException]":
        """
        Delete a env from the database.

        Args:
            env_id: int

        Returns:
            views.EnvDeleted

        Raises:
            HTTP 404 Not Found: If the env is not found in the database.
        """
        env_repo = EnvRepository(env_id=env_id)
        try:
            await env_repo.delete_env()
        except Exception as e:
            exc_str = parse_error(e)
            logging.error(
                f"[{datetime.now()}] controllers.environment.delete_env: {exc_str}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete environment: {e}",
            ) from e
        else:
            return EnvDeleted(deleted_env_id=env_id)
        finally:
            logging.info(
                f"[{datetime.now()}] Call to controllers.environment.delete_env completed; params: EnvID {env_id}"
            )

    @classmethod
    async def simulate(cls, env_id: int) -> "Union[EnvSummary, HTTPException]":
        """
        Simulate a rocket environment.

        Args:
            env_id: int.

        Returns:
            views.EnvSummary

        Raises:
            HTTP 404 Not Found: If the env does not exist in the database.
        """
        read_env = await cls.get_env_by_id(env_id)
        try:
            rocketpy_env = cls.get_rocketpy_env(read_env)
            env_simulation_numbers = EnvData.parse_obj(
                rocketpy_env.all_info_returned()
            )
            env_simulation_plots = EnvPlots.parse_obj(
                rocketpy_env.all_plot_info_returned()
            )
            env_summary = EnvSummary(
                env_data=env_simulation_numbers, env_plots=env_simulation_plots
            )
        except Exception as e:
            exc_str = parse_error(e)
            logging.error(
                f"[{datetime.now()}] controllers.environment.simulate: {exc_str}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to simulate environment: {e}",
            ) from e
        else:
            return env_summary
        finally:
            logging.info(
                f"[{datetime.now()}] Call to controllers.environment.simulate completed; params: EnvID {env_id}"
            )
