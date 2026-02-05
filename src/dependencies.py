from functools import cache
from typing import Annotated

from fastapi import Depends

from src.controllers.rocket import RocketController
from src.controllers.motor import MotorController
from src.controllers.environment import EnvironmentController
from src.controllers.flight import FlightController

@cache
def get_rocket_controller() -> RocketController:
    """
    Provides a singleton RocketController instance.
    
    The controller is stateless and can be safely reused across requests.
    Using cache ensures thread-safe singleton behavior.
    
    Returns:
        RocketController: Shared controller instance for rocket operations.
    """
    return RocketController()


@cache
def get_motor_controller() -> MotorController:
    """
    Provides a singleton MotorController instance.
    
    Returns:
        MotorController: Shared controller instance for motor operations.
    """
    return MotorController()


@cache
def get_environment_controller() -> EnvironmentController:
    """
    Provides a singleton EnvironmentController instance.
    
    Returns:
        EnvironmentController: Shared controller instance for environment operations.
    """
    return EnvironmentController()


@cache
def get_flight_controller() -> FlightController:
    """
    Provides a singleton FlightController instance.
    
    Returns:
        FlightController: Shared controller instance for flight operations.
    """
    return FlightController()

RocketControllerDep = Annotated[RocketController, Depends(get_rocket_controller)]
MotorControllerDep = Annotated[MotorController, Depends(get_motor_controller)]
EnvironmentControllerDep = Annotated[
    EnvironmentController, Depends(get_environment_controller)
]
FlightControllerDep = Annotated[FlightController, Depends(get_flight_controller)]
