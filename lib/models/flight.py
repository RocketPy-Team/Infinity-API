from typing import Optional, Self, ClassVar, Literal
from lib.models.interface import ApiBaseModel
from lib.models.rocket import RocketModel
from lib.models.environment import EnvironmentModel


class FlightModel(ApiBaseModel):
    NAME: ClassVar = "flight"
    METHODS: ClassVar = ("POST", "GET", "PUT", "DELETE")

    name: str = "flight"
    environment: EnvironmentModel
    rocket: RocketModel
    rail_length: float = 1
    time_overshoot: bool = True
    terminate_on_apogee: bool = True
    equations_of_motion: Literal['standard', 'solid_propulsion'] = 'standard'

    # Optional parameters
    inclination: Optional[int] = None
    heading: Optional[int] = None
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
        from lib.views.flight import FlightUpdated

        return FlightUpdated()

    @staticmethod
    def DELETED():
        from lib.views.flight import FlightDeleted

        return FlightDeleted()

    @staticmethod
    def CREATED(model_id: str):
        from lib.views.flight import FlightCreated

        return FlightCreated(flight_id=model_id)

    @staticmethod
    def RETRIEVED(model_instance: type(Self)):
        from lib.views.flight import FlightRetrieved, FlightView

        return FlightRetrieved(
            flight=FlightView(
                flight_id=model_instance.get_id(),
                **model_instance.model_dump(),
            )
        )
