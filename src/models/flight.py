from typing import Optional, Self, ClassVar, Literal

from pydantic import BaseModel, Field
from src.models.interface import ApiBaseModel
from src.models.rocket import RocketModel
from src.models.environment import EnvironmentModel


class FlightModel(ApiBaseModel):
    NAME: ClassVar = "flight"
    METHODS: ClassVar = ("POST", "GET", "PUT", "DELETE")

    name: str = "flight"
    environment: EnvironmentModel
    rocket: RocketModel
    rail_length: float = 1
    time_overshoot: bool = True
    terminate_on_apogee: bool = False
    equations_of_motion: Literal['standard', 'solid_propulsion'] = 'standard'

    # Optional parameters
    inclination: float = 90.0
    heading: float = 0.0
    # TODO: implement initial_solution
    max_time: Optional[int] = None
    max_time_step: Optional[float] = None
    min_time_step: Optional[int] = None
    rtol: Optional[float] = None
    atol: Optional[float] = None
    verbose: Optional[bool] = None

    def get_additional_parameters(self):
        return {
            key: value
            for key, value in self.dict().items()
            if value is not None
            and key
            not in [
                "flight_id",
                "name",
                "environment",
                "rocket",
                "rail_length",
                "time_overshoot",
                "terminate_on_apogee",
                "equations_of_motion",
            ]
        }

    @staticmethod
    def UPDATED():
        return

    @staticmethod
    def DELETED():
        return

    @staticmethod
    def CREATED(model_id: str):
        from src.views.flight import FlightCreated

        return FlightCreated(flight_id=model_id)

    @staticmethod
    def RETRIEVED(model_instance: type(Self)):
        from src.views.flight import FlightRetrieved, FlightView

        return FlightRetrieved(
            flight=FlightView(
                flight_id=model_instance.get_id(),
                **model_instance.model_dump(),
            )
        )


class FlightPartialModel(BaseModel):
    """Flight attributes required when rocket/environment are referenced."""

    name: str = Field(default="flight")
    rail_length: float = 1
    time_overshoot: bool = True
    terminate_on_apogee: bool = False
    equations_of_motion: Literal['standard', 'solid_propulsion'] = 'standard'
    inclination: float = 90.0
    heading: float = 0.0
    max_time: Optional[int] = None
    max_time_step: Optional[float] = None
    min_time_step: Optional[int] = None
    rtol: Optional[float] = None
    atol: Optional[float] = None
    verbose: Optional[bool] = None

    def assemble(
        self,
        *,
        environment: EnvironmentModel,
        rocket: RocketModel,
    ) -> FlightModel:
        """Compose a full flight model using referenced resources."""

        flight_data = self.model_dump(exclude_none=True)
        return FlightModel(
            environment=environment,
            rocket=rocket,
            **flight_data,
        )


class FlightWithReferencesRequest(BaseModel):
    """Payload for creating or updating flights via component references."""

    environment_id: str
    rocket_id: str
    flight: FlightPartialModel
