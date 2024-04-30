from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from lib.secrets import secrets_instance


class Repository:
    """
    Base class for all repositories (singleton)
    """

    _self = None

    def __new__(cls, *args, **kwargs):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self

    def __init__(self, collection: str):
        self.connection_string = secrets_instance.get_secret(
            "MONGODB_CONNECTION_STRING"
        )
        self.client = AsyncIOMotorClient(
            self.connection_string, server_api=ServerApi("1")
        )
        self.db = self.client.rocketpy
        self.collection = self.db[collection]

    async def close_connection(self) -> None:
        self.client.close()
