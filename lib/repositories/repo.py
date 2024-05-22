import threading
from lib.secrets import Secrets
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi


class Repository:
    """
    Base class for all repositories (singleton)
    """

    _instances = {}
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super(Repository, cls).__new__(cls)
                cls._instances[cls]._initialized = False  # Initialize here
        return cls._instances[cls]

    def __init__(self, collection: str):
        if not self._initialized:
            self._connection_string = Secrets.get_secret(
                "MONGODB_CONNECTION_STRING"
            )
            self._client = AsyncIOMotorClient(
                self.connection_string,
                server_api=ServerApi("1"),
                maxIdleTimeMS=5000,
                connectTimeoutMS=5000,
                serverSelectionTimeoutMS=30000,
            )
            self._collection = self.client.rocketpy[collection]
            self._initialized = True  # Mark as initialized

    @property
    def connection_string(self):
        return self._connection_string

    @connection_string.setter
    def connection_string(self, value):
        self._connection_string = value

    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, value):
        self._client = value

    @property
    def collection(self):
        return self._collection

    @collection.setter
    def collection(self, value):
        self._collection = value

    async def close_connection(self) -> None:
        self.client.close()
