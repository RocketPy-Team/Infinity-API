from typing import Self

import dill

from rocketpy.environment.environment import Environment as RocketPyEnvironment
from src.models.environment import EnvironmentModel
from src.views.environment import EnvironmentSimulation
from src.utils import collect_attributes


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
        # RocketPy guards pressure/temperature against None but NOT wind, so a
        # custom_atmosphere with wind_u/wind_v left unset raises
        # "'NoneType' object has no attribute 'shape'". Default missing wind to 0
        # (only None is replaced — real 0.0 values and wind profiles pass through).
        rocketpy_env.set_atmospheric_model(
            type=env.atmospheric_model_type,
            file=env.atmospheric_model_file,
            pressure=env.pressure,
            temperature=env.temperature,
            wind_u=env.wind_u if env.wind_u is not None else 0.0,
            wind_v=env.wind_v if env.wind_v is not None else 0.0,
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

        encoded_attributes = collect_attributes(
            self.environment,
            [EnvironmentSimulation],
        )
        env_simulation = EnvironmentSimulation(**encoded_attributes)
        return env_simulation

    def get_environment_binary(self) -> bytes:
        """
        Get the binary representation of the environment.

        Returns:
            bytes
        """
        return dill.dumps(self.environment)
