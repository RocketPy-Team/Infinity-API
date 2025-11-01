import importlib
import asyncio
import threading
import functools

from typing import Self
from tenacity import (
    stop_after_attempt,
    wait_fixed,
    retry,
)
from pydantic import ValidationError
from pymongo.errors import PyMongoError
from pymongo.server_api import ServerApi
from pymongo import AsyncMongoClient

from fastapi import HTTPException, status
from bson import ObjectId

from src import logger
from src.secrets import Secrets
from src.models.interface import ApiBaseModel


def not_implemented(*args, **kwargs):
    raise NotImplementedError("Method not implemented.")


class RepositoryNotInitializedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Repository not initialized. Please try again later.",
        )


def repository_exception_handler(method):
    """
    Decorator that standardizes error handling and logging for repository coroutine methods.

    Parameters:
        method (Callable): The asynchronous repository method to wrap.

    Returns:
        wrapper (Callable): An async wrapper that:
            - re-raises PyMongoError after logging the exception,
            - re-raises RepositoryNotInitializedException after logging the exception,
            - logs any other exception and raises an HTTPException with status 500 and detail 'Unexpected error ocurred',
            - always logs completion of the repository method call with the repository name, method name, and kwargs.
    """

    @functools.wraps(method)
    async def wrapper(self, *args, **kwargs):
        try:
            return await method(self, *args, **kwargs)
        except PyMongoError as e:
            logger.exception(f"{method.__name__} - caught PyMongoError: {e}")
            raise
        except RepositoryNotInitializedException as e:
            logger.exception(
                f"{method.__name__} - Repository not initialized: {e}"
            )
            raise
        except Exception as e:
            logger.exception(
                f"{method.__name__} - caught unexpected error: {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Unexpected error ocurred',
            ) from e
        finally:
            logger.info(
                f"Call to repositories.{self.model.NAME}.{method.__name__} completed for {kwargs}"
            )

    return wrapper


class RepositoryInterface:
    """
    Interface class for all repositories (singleton)

    This class is used to define the common attributes and
    methods that all repositories should have.

    The class is a singleton, meaning that only one instance
    of the class is created and shared among all instances
    of the class. This is done to ensure that only one
    connection per collection in the database is created
    and shared among all repositories.
    """

    _global_instances = {}
    _global_thread_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        """
        Ensure a single thread-safe instance exists for the subclass.

        Creates and returns the singleton instance for this subclass, creating it if absent while holding a global thread lock to prevent concurrent instantiation.

        Returns:
            The singleton instance of the subclass.
        """
        with cls._global_thread_lock:
            if cls not in cls._global_instances:
                instance = super().__new__(cls)
                cls._global_instances[cls] = instance
        return cls._global_instances[cls]

    def __init__(self, model: ApiBaseModel, *, max_pool_size: int = 3):
        """
        Initialize the repository instance for a specific API model and configure its connection pool.

        Parameters:
            model (ApiBaseModel): The API model used for validation and to determine the repository's collection.
            max_pool_size (int, optional): Maximum size of the MongoDB connection pool. Defaults to 3.

        Notes:
            If the instance is already initialized, this constructor will not reconfigure it. Initialization of the underlying connection is started asynchronously.
        """
        if not getattr(self, '_initialized', False):
            self.model = model
            self._max_pool_size = max_pool_size
            self._initialized_event = asyncio.Event()
            self._initialize()

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(0.2))
    async def _async_init(self):
        """
        Perform idempotent, retry-safe asynchronous initialization of the repository instance.

        Ensures a per-instance asyncio.Lock exists and acquires it to run initialization exactly once; on success it marks the instance as initialized and sets the internal _initialized_event so awaiters can proceed. If initialization fails, the original exception from _initialize_connection is propagated after logging.
        """
        if getattr(self, '_initialized', False):
            return

        if not hasattr(self, '_init_lock'):
            self._init_lock = asyncio.Lock()

        async with self._init_lock:
            if getattr(self, '_initialized', False):
                return

            try:
                self._initialize_connection()
            except Exception as e:
                logger.error("Initialization failed: %s", e, exc_info=True)
                self._initialized = False
                raise

            self._initialized = True
            self._initialized_event.set()

    def _initialize(self):
        """
        Ensure the repository's asynchronous initializer is executed: run it immediately if no event loop is active, otherwise schedule it on the running loop.

        If there is no running asyncio event loop, this method runs self._async_init() to completion on the current thread, blocking until it finishes. If an event loop is running, it schedules self._async_init() as a background task on that loop and returns immediately.
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(self._async_init())
        else:
            loop.create_task(self._async_init())

    async def __aenter__(self):
        """
        Waits for repository initialization to complete and returns the repository instance.

        Returns:
            RepositoryInterface: The initialized repository instance.
        """
        await self._initialized_event.wait()  # Ensure initialization is complete
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._initialized_event.wait()

    def _initialize_connection(self):
        """
        Initialize the MongoDB async client, store the connection string, and bind the collection for this repository instance.

        This method fetches the MongoDB connection string from secrets, creates an AsyncMongoClient configured with pool and timeout settings, and sets self._collection to the repository's collection named by the model. On success it logs the initialized client; on failure it raises a ConnectionError.

        Raises:
            ConnectionError: If the client or collection cannot be initialized.
        """
        try:
            self._connection_string = Secrets.get_secret(
                "MONGODB_CONNECTION_STRING"
            )
            self._client = AsyncMongoClient(
                self._connection_string,
                server_api=ServerApi("1"),
                maxIdleTimeMS=30000,
                minPoolSize=1,
                maxPoolSize=self._max_pool_size,
                serverSelectionTimeoutMS=60000,
            )
            self._collection = self._client.rocketpy[self.model.NAME]
            logger.info(
                "AsyncMongoClient initialized for %s",
                self.__class__,
            )
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

    @classmethod
    def get_model_repo(cls, model: ApiBaseModel) -> Self:
        repo_path = cls.__module__.replace('interface', f'{model.NAME}')
        return getattr(
            importlib.import_module(repo_path),
            f"{model.NAME.capitalize()}Repository",
        )

    @repository_exception_handler
    async def insert(self, data: dict):
        collection = self.get_collection()
        try:
            self.model.model_validate(data)
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=str(e))
        result = await collection.insert_one(data)
        return str(result.inserted_id)

    @repository_exception_handler
    async def update_by_id(self, data: dict, *, data_id: str):
        collection = self.get_collection()
        assert self.model.model_validate(data)
        await collection.update_one({"_id": ObjectId(data_id)}, {"$set": data})
        return self

    @repository_exception_handler
    async def find_by_id(self, *, data_id: str):
        collection = self.get_collection()
        read_data = await collection.find_one({"_id": ObjectId(data_id)})
        if read_data:
            parsed_model = self.model.model_validate(read_data)
            parsed_model.set_id(str(read_data["_id"]))
            return parsed_model
        return None

    @repository_exception_handler
    async def delete_by_id(self, *, data_id: str):
        collection = self.get_collection()
        await collection.delete_one({"_id": ObjectId(data_id)})
        return self

    @repository_exception_handler
    async def find_by_query(self, query: dict):
        collection = self.get_collection()
        parsed_models = []
        async for read_data in collection.find(query):
            parsed_model = self.model.model_validate(read_data)
            parsed_model.set_id(str(read_data["_id"]))
            parsed_models.append(parsed_model)
        return parsed_models
