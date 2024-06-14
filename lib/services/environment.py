from typing import Self
from rocketpy.environment.environment import Environment as RocketPyEnvironment
from rocketpy.utilities import get_instance_attributes
from lib.models.environment import Env
from lib.views.environment import EnvSummary


class EnvironmentService(RocketPyEnvironment):

    @classmethod
    def from_env_model(cls, env: Env) -> Self:
        """
        Get the rocketpy env object.

        Returns:
            RocketPyEnvironment
        """
        rocketpy_env = cls(
            latitude=env.latitude,
            longitude=env.longitude,
            elevation=env.elevation,
            date=env.date,
        )
        rocketpy_env.set_atmospheric_model(
            type=env.atmospheric_model_type, file=env.atmospheric_model_file
        )
        return rocketpy_env

    def get_env_summary(self) -> EnvSummary:
        """
        Get the summary of the environment.

        Returns:
            EnvSummary
        """

        attributes = get_instance_attributes(self)
        env_summary = EnvSummary(**attributes)
        return env_summary
