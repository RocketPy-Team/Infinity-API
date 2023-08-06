from rocketpy import Environment

from lib.models.environment import Env
from lib.repositories.environment import EnvRepository
from lib.views import EnvSummary, EnvData, EnvPlots

from fastapi import Response, status
from typing import Dict, Any, Union

import jsonpickle

class EnvController(): 
    """ 
    Controller for the Environment model.

    Init Attributes:
        env (models.Env): Environment model object.

    Enables:
        - Create a rocketpy.Environment object from an Env model object.
    """
    def __init__(self, env: Env):
        rocketpy_env = Environment(
                railLength=env.railLength,
                latitude=env.latitude,
                longitude=env.longitude,
                elevation=env.elevation,
                date=env.date
                )
        rocketpy_env.setAtmosphericModel(
                type=env.atmosphericModelType, 
                file=env.atmosphericModelFile
                )
        self.rocketpy_env = rocketpy_env 
        self.env = env

    def create_env(self) -> "Dict[str, str]":
        """
        Create a env in the database.

        Returns:
            Dict[str, str]: Environment id.
        """
        env = EnvRepository(environment=self.env)
        successfully_created_env = env.create_env()
        if successfully_created_env: 
            return { "message": "env created", "env_id": env.env_id }
        else:
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_env(env_id: int) -> "Union[Env, Response]":
        """
        Get a env from the database.

        Args:
            env_id (int): Environment id.

        Returns:
            env model object

        Raises:
            HTTP 404 Not Found: If the env is not found in the database. 
        """
        successfully_read_env = EnvRepository(env_id=env_id).get_env()
        if not successfully_read_env:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
        return successfully_read_env

    def get_rocketpy_env(env_id: int) -> "Union[Dict[str, Any], Response]":
        """
        Get a rocketpy env object encoded as jsonpickle string from the database.

        Args:
            env_id (int): env id.

        Returns:
            str: jsonpickle string of the rocketpy env.

        Raises:
            HTTP 404 Not Found: If the env is not found in the database.
        """
        successfully_read_env = EnvRepository(env_id=env_id).get_env()
        if not successfully_read_env:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        successfully_read_rocketpy_env  = EnvController( successfully_read_env ).rocketpy_env

        return { "jsonpickle_rocketpy_env": jsonpickle.encode(successfully_read_rocketpy_env) }

           
    def update_env(self, env_id: int) -> "Union[Dict[str, Any], Response]":
        """
        Update a env in the database.

        Args:
            env_id (int): env id.

        Returns:
            Dict[str, Any]: env id and message.

        Raises:
            HTTP 404 Not Found: If the env is not found in the database.
        """
        successfully_read_env = EnvRepository(env_id=env_id).get_env()
        if not successfully_read_env:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        successfully_updated_env = \
                EnvRepository(environment=self.env, env_id=env_id).update_env()

        if successfully_updated_env:
            return { 
                    "message": "env updated successfully", 
                    "new_env_id": successfully_updated_env
            }
        else:
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete_env(env_id: int) -> "Union[Dict[str, str], Response]":
        """
        Delete a env from the database.

        Args:
            env_id (int): Environment id.

        Returns:
            Dict[str, str]: Environment id and message.

        Raises:
            HTTP 404 Not Found: If the env is not found in the database.
        """
        successfully_read_env = EnvRepository(env_id=env_id).get_env()
        if not successfully_read_env:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        successfully_deleted_env = EnvRepository(env_id=env_id).delete_env()
        if successfully_deleted_env: 
            return {"env_id": env_id, "message": "env deleted successfully"}
        else:
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def simulate(env_id: int) -> "Union[EnvSummary, Response]":
        """
        Simulate a rocket environment.

        Args:
            env_id (int): Env id.

        Returns:
            Env summary view.

        Raises:
            HTTP 404 Not Found: If the env does not exist in the database.
        """
        successfully_read_env = EnvRepository(env_id=env_id).get_env()
        if not successfully_read_env:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        env = EnvController(successfully_read_env).rocketpy_env
        env_simulation_numbers = EnvData.parse_obj(env.allInfoReturned())
        env_simulation_plots = EnvPlots.parse_obj(env.allPlotInfoReturned())

        env_summary = EnvSummary( data=env_simulation_numbers, plots=env_simulation_plots )

        return env_summary
