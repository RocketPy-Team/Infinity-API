from typing import Self

import dill

from rocketpy.environment.environment import Environment as RocketPyEnvironment
from rocketpy.utilities import get_instance_attributes
from lib.models.environment import EnvironmentModel
from lib.views.environment import EnvironmentSimulation


class EnvironmentService:
    _environment: RocketPyEnvironment

    def __init__(self, environment: RocketPyEnvironment = None):
        self._environment = environment

    @classmethod
    def from_env_model(cls, env: EnvironmentModel) -> Self:
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
            type=env.atmospheric_model_type,
            file=env.atmospheric_model_file,
        )
        return cls(environment=rocketpy_env)

    @property
    def environment(self) -> RocketPyEnvironment:
        return self._environment

    @environment.setter
    def environment(self, environment: RocketPyEnvironment):
        self._environment = environment

    def get_environment_simulation(self) -> EnvironmentSimulation:
        """
        Get the simulation of the environment.

        Returns:
            EnvironmentSimulation
        """

        attributes = get_instance_attributes(self.environment)
        env_simulation = EnvironmentSimulation(**attributes)
        return env_simulation

    def get_environment_binary(self) -> bytes:
        """
        Get the binary representation of the environment.

        Returns:
            bytes
        """
        return dill.dumps(self.environment)
