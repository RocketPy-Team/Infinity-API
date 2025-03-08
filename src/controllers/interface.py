import functools
from typing import List
from pymongo.errors import PyMongoError
from fastapi import HTTPException, status

from src import logger
from src.models.interface import ApiBaseModel
from src.views.interface import ApiBaseView
from src.repositories.interface import RepositoryInterface


def controller_exception_handler(method):
    @functools.wraps(method)
    async def wrapper(self, *args, **kwargs):
        try:
            return await method(self, *args, **kwargs)
        except PyMongoError:
            logger.error(f"{method.__name__}: PyMongoError")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Operation failed, please try again later",
            )
        except HTTPException as e:
            raise e from e
        except Exception as e:
            logger.exception(f"{method.__name__}: Unexpected error {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected error",
            )
        finally:
            logger.info(
                f"Call to {method.__name__} completed for {self.__class__.__name__}"
            )

    return wrapper


class ControllerBase:

    def __init__(self, models: List[ApiBaseModel]):
        self._initialized_models = {}
        self._load_models(models)

    def _load_models(self, models: List[ApiBaseModel]):
        for model in models:
            self._initialized_models[model.NAME] = model

            for action in model.METHODS:
                method_name = (
                    f"{action.lower()}_{model.NAME}"
                    if action == "POST"
                    else f"{action.lower()}_{model.NAME}_by_id"
                )
                method = self._generate_method(action.lower(), model)
                setattr(self, method_name, method)

    def _generate_method(self, action: str, model: ApiBaseModel):
        async def method(*args, **kwargs):
            handler = getattr(self, f"_{action}_model", None)
            if handler:
                model_repo = RepositoryInterface.get_model_repo(model)
                return await handler(  # pylint: disable=not-callable
                    model, model_repo, *args, **kwargs
                )
            raise NotImplementedError(f"_{action}_model is not implemented")

        return method

    @controller_exception_handler
    async def _post_model(
        self,
        model: ApiBaseModel,
        model_repo: RepositoryInterface,
        model_instance: ApiBaseModel,
    ) -> ApiBaseView:
        async with model_repo() as repo:
            inserted_id = await getattr(repo, f'create_{model.NAME}')(
                model_instance
            )
            return model.CREATED(inserted_id)

    @controller_exception_handler
    async def _get_model(
        self,
        model: ApiBaseModel,
        model_repo: RepositoryInterface,
        model_id: str,
    ) -> ApiBaseView:
        async with model_repo() as repo:
            model_instance = await getattr(repo, f'read_{model.NAME}_by_id')(
                model_id
            )
            if model_instance:
                return model.RETRIEVED(model_instance)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{model.NAME} not found",
            )

    @controller_exception_handler
    async def _put_model(
        self,
        model: ApiBaseModel,
        model_repo: RepositoryInterface,
        model_id: str,
        model_instance: ApiBaseModel,
    ) -> ApiBaseView:
        async with model_repo() as repo:
            await getattr(repo, f'update_{model.NAME}_by_id')(
                model_id, model_instance
            )
            return model.UPDATED()

    @controller_exception_handler
    async def _delete_model(
        self,
        model: ApiBaseModel,
        model_repo: RepositoryInterface,
        model_id: str,
    ) -> ApiBaseView:
        async with model_repo() as repo:
            await getattr(repo, f'delete_{model.NAME}_by_id')(model_id)
            return model.DELETED()
