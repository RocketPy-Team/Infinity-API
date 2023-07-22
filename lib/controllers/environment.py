class EnvController(): 
    """ 
    Controller for the Environment model.

    Init Attributes:
        env (models.Env): Environment model object.

    Enables:
        - Create a rocketpy.Environment object from an Env model object.
    """
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
        self.rocketpy_env = rocketpy_env 
        self.env = env

