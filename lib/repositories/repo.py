import asyncio
import threading

from tenacity import (
    stop_after_attempt,
    wait_fixed,
    retry,
)
from pydantic import BaseModel
from pymongo.server_api import ServerApi
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import HTTPException, status

from lib import logger
from lib.secrets import Secrets


class RepositoryNotInitializedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Repository not initialized. Please try again later.",
        )


class RepoInstances(BaseModel):
    instance: object
    prospecting: int = 0

    def add_prospecting(self):
        self.prospecting += 1

    def remove_prospecting(self):
        self.prospecting -= 1

    def get_prospecting(self):
        return self.prospecting

    def get_instance(self):
        return self.instance


class Repository:
    """
    Base class for all repositories (singleton)
    """

    _global_instances = {}
    _global_thread_lock = threading.RLock()
    _global_async_lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs):
        with (
            cls._global_thread_lock
        ):  # Ensure thread safety for singleton instance creation
            if cls not in cls._global_instances:
                instance = super(Repository, cls).__new__(cls)
                cls._global_instances[cls] = RepoInstances(instance=instance)
            else:
                cls._global_instances[cls].add_prospecting()
        return cls._global_instances[cls].get_instance()

    @classmethod
    def _stop_prospecting(cls):
        if cls in cls._global_instances:
            cls._global_instances[cls].remove_prospecting()

    @classmethod
    def _get_instance_prospecting(cls):
        if cls in cls._global_instances:
            return cls._global_instances[cls].get_prospecting()
        return 0

    def __init__(self, collection_name: str, *, max_pool_size: int = 10):
        if not getattr(self, '_initialized', False):
            self._max_pool_size = max_pool_size
            self._collection_name = collection_name
            self._initialized_event = asyncio.Event()
            self._initialize()

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(0.2))
    async def _async_init(self):
        async with (
            self._global_async_lock
        ):  # Hybrid safe locks for initialization
            with self._global_thread_lock:
                try:
                    self._initialize_connection()
                    self._initialized = True
                except Exception as e:
                    logger.error("Initialization failed: %s", e, exc_info=True)
                    self._initialized = False

    def _on_init_done(self, future):
        try:
            future.result()
        finally:
            self._initialized_event.set()

    def _initialize(self):
        if not asyncio.get_event_loop().is_running():
            asyncio.run(self._async_init())
        else:
            loop = asyncio.get_event_loop()
            loop.create_task(self._async_init()).add_done_callback(
                self._on_init_done
            )

    def __del__(self):
        with self._global_thread_lock:
            self._global_instances.pop(self.__class__, None)
            self._initialized = False
            self._stop_prospecting()

    async def __aenter__(self):
        await self._initialized_event.wait()  # Ensure initialization is complete
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._initialized_event.wait()

    def _initialize_connection(self):
        try:
            self._connection_string = Secrets.get_secret(
                "MONGODB_CONNECTION_STRING"
            )
            self._client = AsyncIOMotorClient(
                self._connection_string,
                server_api=ServerApi("1"),
                maxIdleTimeMS=30000,
                minPoolSize=10,
                maxPoolSize=self._max_pool_size,
                serverSelectionTimeoutMS=60000,
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

    def _get_connection_string(self):
        if not getattr(self, '_initialized', False):
            raise RepositoryNotInitializedException()
        return self._connection_string

    @property
    def connection_string(self):
        return self._get_connection_string()

    def _get_client(self):
        if not getattr(self, '_initialized', False):
            raise RepositoryNotInitializedException()
        return self._client

    @property
    def client(self):
        return self._get_client()

    def get_collection(self):
        if not getattr(self, '_initialized', False):
            raise RepositoryNotInitializedException()
        return self._collection
