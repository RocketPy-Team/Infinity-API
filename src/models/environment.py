import datetime
from typing import Optional, ClassVar, Self, Literal
from src.models.interface import ApiBaseModel


class EnvironmentModel(ApiBaseModel):
    NAME: ClassVar = 'environment'
    METHODS: ClassVar = ('POST', 'GET', 'PUT', 'DELETE')
    latitude: float
    longitude: float
    elevation: Optional[float] = 0.0

    # Optional parameters
    atmospheric_model_type: Literal[
        'standard_atmosphere',
        'custom_atmosphere',
        'wyoming_sounding',
        'forecast',
        'reanalysis',
        'ensemble',
    ] = 'standard_atmosphere'
    atmospheric_model_file: Optional[str] = None
    date: Optional[datetime.datetime] = (
        datetime.datetime.today() + datetime.timedelta(days=1)
    )

    @staticmethod
    def UPDATED():
        return

    @staticmethod
    def DELETED():
        return

    @staticmethod
    def CREATED(model_id: str):
        from src.views.environment import EnvironmentCreated

        return EnvironmentCreated(environment_id=model_id)

    @staticmethod
    def RETRIEVED(model_instance: type(Self)):
        from src.views.environment import EnvironmentRetrieved, EnvironmentView

        return EnvironmentRetrieved(
            environment=EnvironmentView(
                environment_id=model_instance.get_id(),
                **model_instance.model_dump(),
            )
        )
