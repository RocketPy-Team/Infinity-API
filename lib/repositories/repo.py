import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from lib import logger
from lib.secrets import Secrets


class Repository:
    """
    Base class for all repositories (singleton)
    """

    _instances = {}
    _lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super(Repository, cls).__new__(cls)
            cls._instances[cls] = instance
        return cls._instances[cls]

    def __init__(self, collection_name: str):
        if not getattr(self, '_initialized', False):
            self._collection_name = collection_name
            self._initialized_event = asyncio.Event()
            if not asyncio.get_event_loop().is_running():
                asyncio.run(self._async_init())
            else:
                loop = asyncio.get_event_loop()
                loop.create_task(self._async_init()).add_done_callback(
                    self._on_init_done
                )

    def _on_init_done(self, future):
        try:
            future.result()
        except Exception as e:
            logger.error("Initialization failed: %s", e, exc_info=True)
            raise e from e

    async def _async_init(self):
        async with self._lock:
            self._initialize_connection()
            self._initialized = True
            self._initialized_event.set()

    async def __aenter__(self):
        await self._initialized_event.wait()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._initialized_event.wait()
        async with self._lock:
            self._cleanup_instance()

    def _initialize_connection(self):
        try:
            self._connection_string = Secrets.get_secret(
                "MONGODB_CONNECTION_STRING"
            )
            self._client = AsyncIOMotorClient(
                self._connection_string,
                server_api=ServerApi("1"),
                maxIdleTimeMS=5000,
                connectTimeoutMS=5000,
                serverSelectionTimeoutMS=15000,
            )
            self._collection = self._client.rocketpy[self._collection_name]
            logger.info("MongoDB client initialized for %s", self.__class__)
        except Exception as e:
            logger.error(
                f"Failed to initialize MongoDB client: {e}", exc_info=True
            )
            raise ConnectionError(
                "Could not establish a connection with MongoDB."
            ) from e

    def _cleanup_instance(self):
        if hasattr(self, '_client'):
            self.client.close()
            logger.info("Connection closed for %s", self.__class__)
        self._instances.pop(self.__class__, None)

    @property
    def connection_string(self):
        return self._connection_string

    @connection_string.setter
    def connection_string(self, value):
        self._connection_string = value

    @property
    def client(self):
        if not getattr(self, '_initialized', False):
            raise RuntimeError("Repository not initialized yet")
        return self._client

    @client.setter
    def client(self, value):
        if not getattr(self, '_initialized', False):
            raise RuntimeError("Repository not initialized yet")
        self._client = value

    @property
    def collection(self):
        if not getattr(self, '_initialized', False):
            raise RuntimeError("Repository not initialized yet")
        return self._collection
