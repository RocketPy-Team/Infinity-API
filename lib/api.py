"""
This is the main API file for the RocketPy API.
"""
from typing import Any, Dict

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from lib.views.flight import FlightSummary, FlightCreated, FlightUpdated, FlightDeleted
from lib.views.environment import EnvSummary, EnvCreated, EnvUpdated, EnvDeleted
from lib.views.rocket import RocketSummary, RocketCreated, RocketUpdated, RocketDeleted
from lib.views.motor import MotorSummary, MotorCreated, MotorUpdated, MotorDeleted
from lib.models.environment import Env
from lib.models.flight import Flight
from lib.models.rocket import Rocket
from lib.models.motor import Motor
from lib.controllers.flight import FlightController
from lib.controllers.environment import EnvController
from lib.controllers.rocket import RocketController
from lib.controllers.motor import MotorController

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Flight routes
@app.post("/flights/", tags=["FLIGHT"])
async def create_flight(flight: Flight) -> "FlightCreated":
    """
    Creates a new flight.

    Args:
        Pydantic flight object as a JSON request according to API docs.
    
    Returns:
        HTTP 200 { "message": "Flight created successfully.", id: flight_id_hash }
      
    Raises:
        HTTP 422 Unprocessable Entity: If API is unable to parse flight data, usually happens when some parameter is invalid, please attend to API docs request specifications.
        HTTP 500 Internal Server Error: If API is either unable to create flight in mongoDB or valid parameter type/structure provided but content is breaking the API. 
    """
    return FlightController(flight).create_flight()

@app.get("/flights/{flight_id}", tags=["FLIGHT"])
async def read_flight(flight_id: int) -> "Flight":
    """
    Reads a flight.

    Args:
        flight_id: Flight ID hash.

    Returns:
        Pydantic flight object as JSON.

    Raises:
        HTTP 404 Not Found: If flight_id does not exist in database.
    """
    return FlightController.get_flight(flight_id)

@app.get("/flights/rocketpy/{flight_id}", tags=["FLIGHT"])
async def read_rocketpy_flight(flight_id: int) -> "BaseModel":
    """
    Reads a rocketpy flight object.

    Args:
        flight_id: Flight ID hash.

    Returns:
        RocketPy flight object encoded as a jsonpickle string.

    Raises:
        HTTP 404 Not Found: If flight_id does not exist in database.
    """
    return FlightController.get_rocketpy_flight(flight_id)

@app.put("/flights/{flight_id}/env", tags=["FLIGHT"])
async def update_flight_env(flight_id: int, env: Env) -> "Dict[str, Any]":
    """
    Updates flight environment.

    Args:
        flight_id: Flight ID hash.
        env: Pydantic env object as JSON request according to API docs.

    Returns:
        HTTP 200 { "message": "Flight updated successfully.", new_flight_id: new_flight_id_hash }

    Raises:
        HTTP 404 Not Found: If flight_id does not exist in database.
        HTTP 422 Unprocessable Entity: If API is unable to parse env data, usually happens when some parameter is invalid, please attend to API docs request specifications.
        HTTP 500 Internal Server Error: If API is either unable to update flight in mongoDB or valid parameter type/structure provided but content is breaking the API.
    """
    return FlightController.update_env(flight_id, env)

@app.put("/flights/{flight_id}/rocket", tags=["FLIGHT"])
async def update_flight_rocket(flight_id: int, rocket: Rocket) -> "Dict[str, Any]":
    """
    Updates flight rocket.

    Args:
        flight_id: Flight ID hash.
        rocket: Pydantic rocket object as JSON request according to API docs.

    Returns:
        HTTP 200 { "message": "Flight updated successfully.", new_flight_id: new_flight_id_hash }

    Raises:
        HTTP 404 Not Found: If flight_id does not exist in database.
        HTTP 422 Unprocessable Entity: If API is unable to parse rocket data, usually happens when some parameter is invalid, please attend to API docs request specifications.
        HTTP 500 Internal Server Error: If API is either unable to update flight in mongoDB or valid parameter type/structure provided but content is breaking the API.
    """
    return FlightController.update_rocket(flight_id, rocket)

@app.put("/flights/{flight_id}", tags=["FLIGHT"])
async def update_flight(flight_id: int, flight: Flight) -> "FlightUpdated":
    """
    Updates whole flight.

    Args:
        flight_id: Flight ID hash.
        flight: Pydantic flight object as JSON request according to API docs.

    Returns:
        HTTP 200 { "message": "Flight updated successfully.", new_flight_id: new_flight_id_hash }

    Raises:
        HTTP 404 Not Found: If flight_id does not exist in database.
        HTTP 422 Unprocessable Entity: If API is unable to parse flight data, usually happens when some parameter is invalid, please attend to API docs request specifications.
        HTTP 500 Internal Server Error: If API is either unable to update flight in mongoDB or valid parameter type/structure provided but content is breaking the API.
    """
    return FlightController(flight).update_flight(flight_id)

@app.delete("/flights/{flight_id}", tags=["FLIGHT"])
async def delete_flight(flight_id: int) -> "FlightDeleted":
    """
    Deletes a flight.

    Args:
        flight_id: Flight ID hash.

    Returns:
        HTTP 200 { "message": "Flight deleted successfully." }

    Raises:
        HTTP 404 Not Found: If flight_id does not exist in database.
    """
    return FlightController.delete_flight(flight_id)

@app.get("/flights/{flight_id}/simulate", tags=["FLIGHT"])
async def simulate_flight(flight_id: int) -> "FlightSummary":
    """
    Simulates a flight.

    Args:
        flight_id: Flight ID hash.

    Returns:
        HTTP 200 pydantic flight summary object as JSON.

    Raises:
        HTTP 404 Not Found: If flight_id does not exist in database.
    """
    return FlightController.simulate(flight_id)

# Environment routes
@app.post("/environments/", tags=["ENVIRONMENT"])
async def create_env(env: Env) -> "EnvCreated":
    """
    Creates a new environment.

    Args:
        Pydantic env object as a JSON request according to API docs.
    
    Returns:
        HTTP 200 { "message": "Environment created successfully.", id: env_id_hash }
      
    Raises:
        HTTP 422 Unprocessable Entity: If API is unable to parse env data, usually happens when some parameter is invalid, please attend to API docs request specifications.
        HTTP 500 Internal Server Error: If API is either unable to create env in mongoDB or valid parameter type/structure provided but content is breaking the API. 
    """
    return EnvController(env).create_env()

@app.get("/environments/{env_id}", tags=["ENVIRONMENT"])
async def read_env(env_id: int) -> "Env":
    """
    Reads an environment.

    Args:
        env_id: Environment ID hash.

    Returns:
        Pydantic env object as JSON.

    Raises:
        HTTP 404 Not Found: If env_id does not exist in database.
    """
    return EnvController.get_env(env_id)

@app.put("/environments/{env_id}", tags=["ENVIRONMENT"])
async def update_env(env_id: int, env: Env) -> "EnvUpdated":
    """
    Updates an environment.

    Args:
        env_id: Environment ID hash.
        env: Pydantic env object as JSON request according to API docs.

    Returns:
        HTTP 200 { "message": "Environment updated successfully.", new_env_id: new_env_id_hash }

    Raises:
        HTTP 404 Not Found: If env_id does not exist in database.
        HTTP 422 Unprocessable Entity: If API is unable to parse env data, usually happens when some parameter is invalid, please attend to API docs request specifications.
        HTTP 500 Internal Server Error: If API is either unable to update env in mongoDB or valid parameter type/structure provided but content is breaking the API.
    """
    return EnvController(env).update_env(env_id)

@app.delete("/environments/{env_id}", tags=["ENVIRONMENT"])
async def delete_env(env_id: int) -> "EnvDeleted":
    """
    Deletes an environment.

    Args:
        env_id: Environment ID hash.

    Returns:
        HTTP 200 { "message": "Environment deleted successfully." }

    Raises:
        HTTP 404 Not Found: If env_id does not exist in database.
    """
    return EnvController.delete_env(env_id)

@app.get("/environments/rocketpy/{env_id}", tags=["ENVIRONMENT"])
async def read_rocketpy_env(env_id: int) -> "Dict[str, Any]":
    """
    Reads a rocketpy environment.

    Args:
        env_id: Environment ID hash.

    Returns:
        Rocketpy Environment object encoded as JSONPickle string.

    Raises:
        HTTP 404 Not Found: If env_id does not exist in database.
    """
    return EnvController.get_rocketpy_env(env_id)

@app.get("/environments/{env_id}/simulate", tags=["ENVIRONMENT"])
async def simulate_env(env_id: int) -> "EnvSummary":
    """
    Simulates an environment.

    Args:
        env_id: Env ID hash.

    Returns:
        HTTP 200 pydantic env summary object containig simulation numbers and plots as JSON.

    Raises:
        HTTP 404 Not Found: If env_id does not exist in database.
    """
    return EnvController.simulate(env_id)

# Motor routes
@app.post("/motors/", tags=["MOTOR"])
async def create_motor(motor: Motor) -> "MotorCreated":
    """
    Creates a new motor.

    Args:
        Pydantic motor object as a JSON request according to API docs.
    
    Returns:
        HTTP 200 { "message": "Motor created successfully.", id: motor_id_hash }
      
    Raises:
        HTTP 422 Unprocessable Entity: If API is unable to parse motor data, usually happens when some parameter is invalid, please attend to API docs request specifications.
        HTTP 500 Internal Server Error: If API is either unable to create motor in mongoDB or valid parameter type/structure provided but content is breaking the API. 
    """
    return MotorController(motor).create_motor()

@app.get("/motors/{motor_id}", tags=["MOTOR"])
async def read_motor(motor_id: int) -> "Motor":
    """
    Reads a motor.

    Args:
        motor_id: Motor ID hash.

    Returns:
        Pydantic motor object as JSON.

    Raises:
        HTTP 404 Not Found: If motor_id does not exist in database.
    """
    return MotorController.get_motor(motor_id)

@app.put("/motors/{motor_id}", tags=["MOTOR"])
async def update_motor(motor_id: int, motor: Motor) -> "MotorUpdated":
    """
    Updates a motor.

    Args:
        motor_id: Motor ID hash.
        motor: Pydantic motor object as JSON request according to API docs.

    Returns:
        HTTP 200 { "message": "Motor updated successfully.", new_motor_id: new_motor_id_hash }

    Raises:
        HTTP 404 Not Found: If motor_id does not exist in database.
        HTTP 422 Unprocessable Entity: If API is unable to parse motor data, usually happens when some parameter is invalid, please attend to API docs request specifications.
        HTTP 500 Internal Server Error: If API is either unable to update motor in mongoDB or valid parameter type/structure provided but content is breaking the API.
    """
    return MotorController(motor).update_motor(motor_id)

@app.delete("/motors/{motor_id}", tags=["MOTOR"])
async def delete_motor(motor_id: int) -> "MotorDeleted":
    """
    Deletes a motor.

    Args:
        motor_id: Motor ID hash.

    Returns:
        HTTP 200 { "message": "Motor deleted successfully." }

    Raises:
        HTTP 404 Not Found: If motor_id does not exist in database.
    """
    return MotorController.delete_motor(motor_id)

@app.get("/motors/rocketpy/{motor_id}", tags=["MOTOR"])
async def read_rocketpy_motor(motor_id: int) -> "Dict[str, Any]":
    """
    Reads a rocketpy motor.

    Args:
        motor_id: Motor ID hash.

    Returns:
        Rocketpy Motor object encoded as JSONPickle string.

    Raises:
        HTTP 404 Not Found: If motor_id does not exist in database.
    """
    return MotorController.get_rocketpy_motor(motor_id)

@app.get("/motors/{motor_id}/simulate", tags=["MOTOR"])
async def simulate_motor(motor_id: int) -> "MotorSummary":
    """
    Simulates a motor.

    Args:
        motor_id: Motor ID hash.

    Returns:
        HTTP 200 pydantic motor summary object containig simulation numbers and plots as JSON.

    Raises:
        HTTP 404 Not Found: If motor_id does not exist in database.
    """
    return MotorController.simulate(motor_id)

# Rocket routes
@app.post("/rockets/", tags=["ROCKET"])
async def create_rocket(rocket: Rocket) -> "RocketCreated":
    """
    Creates a new rocket.

    Args:
        Pydantic rocket object as a JSON request according to API docs.
    
    Returns:
        HTTP 200 { "message": "Rocket created successfully.", id: rocket_id_hash }
      
    Raises:
        HTTP 422 Unprocessable Entity: If API is unable to parse rocket data, usually happens when some parameter is invalid, please attend to API docs request specifications.
        HTTP 500 Internal Server Error: If API is either unable to create rocket in mongoDB or valid parameter type/structure provided but content is breaking the API. 
    """
    return RocketController(rocket).create_rocket()

@app.get("/rockets/{rocket_id}", tags=["ROCKET"])
async def read_rocket(rocket_id: int) -> Rocket:
    """
    Reads a rocket.

    Args:
        rocket_id: Rocket ID hash.

    Returns:
        Pydantic rocket object as JSON.

    Raises:
        HTTP 404 Not Found: If rocket_id does not exist in database.
    """
    return RocketController.get_rocket(rocket_id)

@app.put("/rockets/{rocket_id}", tags=["ROCKET"])
async def update_rocket(rocket_id: int, rocket: Rocket) -> "RocketUpdated":
    """
    Updates a rocket.

    Args:
        rocket_id: Rocket ID hash.
        rocket: Pydantic rocket object as JSON request according to API docs.

    Returns:
        HTTP 200 { "message": "Rocket updated successfully.", new_rocket_id: new_rocket_id_hash }

    Raises:
        HTTP 404 Not Found: If rocket_id does not exist in database.
        HTTP 422 Unprocessable Entity: If API is unable to parse rocket data, usually happens when some parameter is invalid, please attend to API docs request specifications.
        HTTP 500 Internal Server Error: If API is either unable to update rocket in mongoDB or valid parameter type/structure provided but content is breaking the API.
    """
    return RocketController(rocket).update_rocket(rocket_id)

@app.delete("/rockets/{rocket_id}", tags=["ROCKET"])
async def delete_rocket(rocket_id: int) -> "RocketDeleted":
    """
    Deletes a rocket.

    Args:
        rocket_id: Rocket ID hash.

    Returns:
        HTTP 200 { "message": "Rocket deleted successfully." }

    Raises:
        HTTP 404 Not Found: If rocket_id does not exist in database.
    """
    return RocketController.delete_rocket(rocket_id)

@app.get("/rockets/rocketpy/{rocket_id}", tags=["ROCKET"])
async def read_rocketpy_rocket(rocket_id: int) -> "Dict[str, Any]":
    """
    Reads a rocketpy rocket.

    Args:
        rocket_id: Rocket ID hash.

    Returns:
        Rocketpy Rocket object encoded as JSONPickle string.

    Raises:
        HTTP 404 Not Found: If rocket_id does not exist in database.
    """
    return RocketController.get_rocketpy_rocket(rocket_id)

@app.get("/rockets/{rocket_id}/simulate", tags=["ROCKET"])
async def simulate_rocket(rocket_id: int) -> "RocketSummary":
    """
    Simulates a rocket.

    Args:
        rocket_id: Rocket ID hash.

    Returns:
        HTTP 200 pydantic rocket summary object containig simulation numbers and plots as JSON.

    Raises:
        HTTP 404 Not Found: If rocket_id does not exist in database.
    """
    return RocketController.simulate(rocket_id)

@app.get("/health", status_code=status.HTTP_200_OK, include_in_schema=False)
async def __perform_healthcheck():
    return {'health': 'Everything OK!'}
