import datetime
from enum import Enum
from typing import Optional, ClassVar, Self
from lib.models.interface import ApiBaseModel


class AtmosphericModelTypes(str, Enum):
    STANDARD_ATMOSPHERE: str = "STANDARD_ATMOSPHERE"
    CUSTOM_ATMOSPHERE: str = "CUSTOM_ATMOSPHERE"
    WYOMING_SOUNDING: str = "WYOMING_SOUNDING"
    FORECAST: str = "FORECAST"
    REANALYSIS: str = "REANALYSIS"
    ENSEMBLE: str = "ENSEMBLE"


class EnvironmentModel(ApiBaseModel):
    NAME: ClassVar = 'environment'
    METHODS: ClassVar = ('POST', 'GET', 'PUT', 'DELETE')
    latitude: float
    longitude: float
    elevation: Optional[int] = 1

    # Optional parameters
    atmospheric_model_type: AtmosphericModelTypes = (
        AtmosphericModelTypes.STANDARD_ATMOSPHERE
    )
    atmospheric_model_file: Optional[str] = None
    date: Optional[datetime.datetime] = (
        datetime.datetime.today() + datetime.timedelta(days=1)
    )

    @staticmethod
    def UPDATED():
        from lib.views.environment import EnvironmentUpdated

        return EnvironmentUpdated()

    @staticmethod
    def DELETED():
        from lib.views.environment import EnvironmentDeleted

        return EnvironmentDeleted()

    @staticmethod
    def CREATED(model_id: str):
        from lib.views.environment import EnvironmentCreated

        return EnvironmentCreated(environment_id=model_id)

    @staticmethod
    def RETRIEVED(model_instance: type(Self)):
        from lib.views.environment import EnvironmentRetrieved, EnvironmentView

        return EnvironmentRetrieved(
            environment=EnvironmentView(
                environment_id=model_instance.get_id(),
                **model_instance.model_dump(),
            )
        )
