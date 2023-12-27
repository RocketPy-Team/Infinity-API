from typing import Union

import jsonpickle
from rocketpy.environment.environment import Environment
from fastapi import HTTPException, status

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
        env (models.Env): Environment model object.

    Enables:
        - Create a rocketpy.Environment object from an Env model object.
    """

    def __init__(self, env: Env):
        rocketpy_env = Environment(
            latitude=env.latitude,
            longitude=env.longitude,
            elevation=env.elevation,
            date=env.date,
        )
        rocketpy_env.set_atmospheric_model(
            type=env.atmospheric_model_type, file=env.atmospheric_model_file
        )
        self.rocketpy_env = rocketpy_env
        self.env = env

    async def create_env(self) -> "Union[EnvCreated, HTTPException]":
        """
        Create a env in the database.

        Returns:
            EnvCreated: Environment id.
        """
        env = EnvRepository(environment=self.env)
        successfully_created_env = await env.create_env()
        if not successfully_created_env:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create environment",
            )

        return EnvCreated(env_id=str(env.env_id))

    @staticmethod
    async def get_env(env_id: int) -> "Union[Env, HTTPException]":
        """
        Get a env from the database.

        Args:
            env_id (int): Environment id.

        Returns:
            env model object

        Raises:
            HTTP 404 Not Found: If the env is not found in the database.
        """
        successfully_read_env = await EnvRepository(env_id=env_id).get_env()
        if not successfully_read_env:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Environment not found"
            )

        return successfully_read_env

    @staticmethod
    async def get_rocketpy_env(env_id: int) -> "Union[EnvPickle, HTTPException]":
        """
        Get a rocketpy env object encoded as jsonpickle string from the database.

        Args:
            env_id (int): env id.

        Returns:
            str: jsonpickle string of the rocketpy env.

        Raises:
            HTTP 404 Not Found: If the env is not found in the database.
        """
        successfully_read_env = await EnvRepository(env_id=env_id).get_env()
        if not successfully_read_env:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Environment not found"
            )

        successfully_read_rocketpy_env = EnvController(
            successfully_read_env
        ).rocketpy_env

        return EnvPickle(
            jsonpickle_rocketpy_env=jsonpickle.encode(successfully_read_rocketpy_env)
        )

    async def update_env(self, env_id: int) -> "Union[EnvUpdated, HTTPException]":
        """
        Update a env in the database.

        Args:
            env_id (int): env id.

        Returns:
            EnvUpdated: env id and message.

        Raises:
            HTTP 404 Not Found: If the env is not found in the database.
        """
        successfully_read_env = await EnvRepository(env_id=env_id).get_env()
        if not successfully_read_env:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Environment not found"
            )

        successfully_updated_env = await EnvRepository(
            environment=self.env, env_id=env_id
        ).update_env()
        if not successfully_updated_env:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update environment",
            )

        return EnvUpdated(new_env_id=str(successfully_updated_env))

    @staticmethod
    async def delete_env(env_id: int) -> "Union[EnvDeleted, HTTPException]":
        """
        Delete a env from the database.

        Args:
            env_id (int): Environment id.

        Returns:
            EnvDeleted: Environment id and message.

        Raises:
            HTTP 404 Not Found: If the env is not found in the database.
        """
        successfully_read_env = await EnvRepository(env_id=env_id).get_env()
        if not successfully_read_env:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Environment not found"
            )

        successfully_deleted_env = await EnvRepository(env_id=env_id).delete_env()
        if not successfully_deleted_env:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete environment",
            )

        return EnvDeleted(deleted_env_id=str(env_id))

    @staticmethod
    async def simulate(env_id: int) -> "Union[EnvSummary, HTTPException]":
        """
        Simulate a rocket environment.

        Args:
            env_id (int): Env id.

        Returns:
            Env summary view.

        Raises:
            HTTP 404 Not Found: If the env does not exist in the database.
        """
        successfully_read_env = await EnvRepository(env_id=env_id).get_env()
        if not successfully_read_env:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Environment not found"
            )

        try:
            env = EnvController(successfully_read_env).rocketpy_env
            env_simulation_numbers = EnvData.parse_obj(env.all_info_returned())
            env_simulation_plots = EnvPlots.parse_obj(env.all_plot_info_returned())
            env_summary = EnvSummary(
                env_data=env_simulation_numbers, env_plots=env_simulation_plots
            )
            return env_summary
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to simulate environment: {e}",
            ) from e
