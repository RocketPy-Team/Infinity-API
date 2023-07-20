from pymongo import MongoClient

class Repository:
    """
    Base class for all repositories (singleton)
    """
    _self = None

    def __new__(cls, *args, **kwargs):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self

    def __init__(self):
        self.connection_string = "***REMOVED***"
        self.client = MongoClient(self.connection_string)
        self.db = self.client.rocketpy
        self.collection = self.db.flights

    def __del__(self):
        self.client.close()
