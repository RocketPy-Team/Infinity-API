from rocketpy import Environment
from lib.models import Flight, Env, Calisto
from lib.views import EnvView, FlightView
import rocketpy.Flight

class EnvController():
    def __init__(self, env: Env):
        rocketpy_env = Environment(
                railLength=env.railLength,
                latitude=env.latitude,
                longitude=env.longitude,
                elevation=env.elevation,
                date=env.date
        )
        rocketpy_env.setAtmosphericModel(
                type=env.atmosphericModelType, 
                file=env.atmosphericModelFile
        )
        self.env = rocketpy_env 

    def view(self):
        return EnvView(self.env)

class FlightController():
    def __init__(self, flight: Flight):
        rocketpy_flight = rocketpy.Flight(
                rocket = Calisto(),
                inclination=flight.inclination, 
                heading=flight.heading,
                environment=EnvController(flight.environment).view().obj
        )
        self.flight = rocketpy_flight 

    def view(self):
        return FlightView(self.flight)
