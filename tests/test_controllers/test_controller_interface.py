from unittest.mock import patch, Mock
import pytest
from pymongo.errors import PyMongoError
from fastapi import HTTPException, status
from lib.controllers.interface import (
    ControllerInterface,
    controller_exception_handler,
)


@pytest.fixture
def stub_model():
    model = Mock()
    model.NAME = 'test_model'
    model.METHODS = ('GET', 'POST', 'PUT', 'DELETE')
    model.UPDATED = lambda: 'Updated'
    model.DELETED = lambda: 'Deleted'
    model.CREATED = lambda arg: 'Created'
    model.RETRIEVED = lambda arg: 'Retrieved'
    return model


@pytest.fixture
def stub_controller(stub_model):
    return ControllerInterface([stub_model])


@pytest.mark.asyncio
async def test_controller_exception_handler_no_exception(stub_model):
    async def method(self, model, *args, **kwargs):  # pylint: disable=unused-argument
        return stub_model, args, kwargs

    test_controller = Mock(method=method)
    method = test_controller.method
    mock_kwargs = {'foo': 'bar'}
    mock_args = ('foo', 'bar')
    wrapped_method = controller_exception_handler(method)
    with patch('lib.controllers.interface.logger') as mock_logger:
        assert await wrapped_method(
            test_controller, stub_model, *mock_args, **mock_kwargs
        ) == (stub_model, mock_args, mock_kwargs)
        mock_logger.error.assert_not_called()
        mock_logger.info.assert_called_once_with(
            "Call to method completed for Mock"
        )


@pytest.mark.asyncio
async def test_controller_exception_handler_db_exception(stub_model):
    async def method(self, model, *args, **kwargs):
        raise PyMongoError

    wrapped_method = controller_exception_handler(method)
    with patch('lib.controllers.interface.logger') as mock_logger:
        with pytest.raises(HTTPException) as exc:
            await wrapped_method(None, stub_model)
        assert exc.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert exc.value.detail == "Operation failed, please try again later"
        mock_logger.error.assert_called_once_with(
            f"{method.__name__}: PyMongoError"
        )


@pytest.mark.asyncio
async def test_controller_exception_handler_http_exception(stub_model):
    async def method(self, model, *args, **kwargs):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Not Found'
        )

    wrapped_method = controller_exception_handler(method)
    with patch('lib.controllers.interface.logger') as mock_logger:
        with pytest.raises(HTTPException) as exc:
            await wrapped_method(None, stub_model)
        assert exc.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc.value.detail == 'Not Found'
        mock_logger.error.assert_not_called()


@pytest.mark.asyncio
async def test_controller_exception_handler_unexpected_exception(stub_model):
    async def method(self, model, *args, **kwargs):
        raise ValueError('Test Error')

    wrapped_method = controller_exception_handler(method)
    with patch('lib.controllers.interface.logger') as mock_logger:
        with pytest.raises(HTTPException) as exc:
            await wrapped_method(None, stub_model)
        assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc.value.detail == 'Unexpected error'
        mock_logger.exception.assert_called_once_with(
            f"{method.__name__}: Unexpected error Test Error"
        )


def test_controller_interface_init(stub_model):
    with patch(
        'lib.controllers.interface.ControllerInterface._generate_method'
    ) as mock_gen:
        mock_gen.return_value = lambda *args, **kwargs: True
        stub_controller = ControllerInterface([stub_model])
        assert stub_controller._initialized_models == {
            'test_model': stub_model
        }
        assert hasattr(stub_controller, 'post_test_model')
        assert hasattr(stub_controller, 'get_test_model_by_id')
        assert hasattr(stub_controller, 'put_test_model_by_id')
        assert hasattr(stub_controller, 'delete_test_model_by_id')
        assert getattr(stub_controller, 'post_test_model')() is True
        assert getattr(stub_controller, 'get_test_model_by_id')() is True
        assert getattr(stub_controller, 'put_test_model_by_id')() is True
        assert getattr(stub_controller, 'delete_test_model_by_id')() is True


@pytest.mark.asyncio
async def test_controller_interface_generate_available_method(
    stub_controller, stub_model
):
    with patch('lib.controllers.interface.RepositoryInterface') as mock_repo:
        with patch(
            'lib.controllers.interface.ControllerInterface._get_model'
        ) as mock_get:
            mock_get.return_value = stub_model
            method = stub_controller._generate_method('get', stub_model)
            assert (
                await method(None, stub_model, mock_repo, 'arg', key='bar')
                == stub_model
            )


@pytest.mark.asyncio
async def test_controller_interface_generate_unavailable_method(
    stub_controller, stub_model
):
    with patch('lib.controllers.interface.RepositoryInterface') as mock_repo:
        with pytest.raises(NotImplementedError):
            method = stub_controller._generate_method('foo', stub_model)
            await method(None, stub_model, mock_repo, 'arg', key='bar')


@pytest.mark.asyncio
async def test_controller_interface_post_model(stub_controller, stub_model):
    with patch('lib.controllers.interface.RepositoryInterface') as mock_repo:
        with patch(
            'lib.controllers.interface.RepositoryInterface.get_model_repo'
        ) as mock_get_repo:
            mock_get_repo.return_value = mock_repo
            assert (
                await stub_controller._post_model(
                    stub_model, mock_repo, stub_model
                )
                == 'Created'
            )


@pytest.mark.asyncio
async def test_controller_interface_get_model_found(
    stub_controller, stub_model
):
    with patch('lib.controllers.interface.RepositoryInterface') as mock_repo:
        with patch(
            'lib.controllers.interface.RepositoryInterface.get_model_repo'
        ) as mock_get_repo:
            mock_get_repo.return_value = mock_repo
            mock_repo.return_value.__aenter__.return_value.read_test_model_by_id.return_value = (
                stub_model
            )
            assert (
                await stub_controller._get_model(stub_model, mock_repo, '123')
                == 'Retrieved'
            )


@pytest.mark.asyncio
async def test_controller_interface_get_model_not_found(
    stub_controller, stub_model
):
    with patch('lib.controllers.interface.RepositoryInterface') as mock_repo:
        with patch(
            'lib.controllers.interface.RepositoryInterface.get_model_repo'
        ) as mock_get_repo:
            mock_get_repo.return_value = mock_repo
            mock_repo.return_value.__aenter__.return_value.read_test_model_by_id.return_value = (
                None
            )
            with pytest.raises(HTTPException) as exc:
                await stub_controller._get_model(stub_model, mock_repo, '123')
            assert exc.value.status_code == status.HTTP_404_NOT_FOUND
            assert exc.value.detail == 'test_model not found'


@pytest.mark.asyncio
async def test_controller_interface_update_model(stub_controller, stub_model):
    with patch('lib.controllers.interface.RepositoryInterface') as mock_repo:
        with patch(
            'lib.controllers.interface.RepositoryInterface.get_model_repo'
        ) as mock_get_repo:
            mock_get_repo.return_value = mock_repo
            mock_repo.return_value.__aenter__.return_value.update_test_model_by_id.return_value = (
                None
            )
            assert (
                await stub_controller._put_model(
                    stub_model, mock_repo, '123', stub_model
                )
                == 'Updated'
            )


@pytest.mark.asyncio
async def test_controller_interface_delete_model(stub_controller, stub_model):
    with patch('lib.controllers.interface.RepositoryInterface') as mock_repo:
        with patch(
            'lib.controllers.interface.RepositoryInterface.get_model_repo'
        ) as mock_get_repo:
            mock_get_repo.return_value = mock_repo
            mock_repo.return_value.__aenter__.return_value.delete_test_model_by_id.return_value = (
                None
            )
            assert (
                await stub_controller._delete_model(
                    stub_model, mock_repo, '123'
                )
                == 'Deleted'
            )
