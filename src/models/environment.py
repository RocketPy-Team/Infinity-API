from datetime import datetime, timezone, timedelta
from typing import Optional, ClassVar, Self, Literal
from pydantic import Field
from src.models.interface import ApiBaseModel


def _default_future_datetime() -> datetime:
    """Factory function to create timezone-aware datetime one day in the future."""
    return datetime.now(timezone.utc) + timedelta(days=1)


class EnvironmentModel(ApiBaseModel):
    NAME: ClassVar = 'environment'
    METHODS: ClassVar = ('POST', 'GET', 'PUT', 'DELETE')
    latitude: float
    longitude: float
    elevation: Optional[float] = 0.0
    pressure: Optional[float | list[tuple[float, float]]] = None
    temperature: Optional[float | list[tuple[float, float]]] = None
    wind_u: Optional[float | list[tuple[float, float]]] = None
    wind_v: Optional[float | list[tuple[float, float]]] = None

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
    date: Optional[datetime] = Field(default_factory=_default_future_datetime)

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
