from unittest.mock import patch, Mock, AsyncMock
import pytest
import pytest_asyncio
from pymongo.errors import PyMongoError
from fastapi import HTTPException, status
from lib.repositories.interface import (
    RepositoryInterface,
    repository_exception_handler,
    RepositoryNotInitializedException,
)


@pytest.fixture
def stub_loaded_model():
    return {'_id': 'mock_id'}


@pytest.fixture
def mock_model():
    return Mock(set_id=Mock())


@pytest_asyncio.fixture
def mock_db_interface(stub_loaded_model):
    async def async_gen(*args, **kwargs):  # pylint: disable=unused-argument
        yield stub_loaded_model
        yield stub_loaded_model

    mock_db_interface = AsyncMock()
    mock_db_interface.find = Mock(return_value=async_gen())
    mock_db_interface.insert_one = AsyncMock(
        return_value=Mock(inserted_id='mock_id')
    )
    mock_db_interface.update_one = AsyncMock(return_value=None)
    mock_db_interface.find_one = AsyncMock(return_value=stub_loaded_model)
    mock_db_interface.delete_one = AsyncMock(return_value=None)
    return mock_db_interface


@pytest_asyncio.fixture
def mock_db_interface_empty_find():
    async def async_gen(*args, **kwargs):  # pylint: disable=unused-argument
        if False:  # pylint: disable=using-constant-test
            yield

    mock_db_interface = AsyncMock()
    mock_db_interface.find = Mock(return_value=async_gen())
    return mock_db_interface


@pytest_asyncio.fixture
def stub_repository(mock_model):
    with patch.object(RepositoryInterface, "_initialize", return_value=None):
        stub_model = Mock(
            NAME='mock_model',
            model_validate=mock_model,
        )
        repo = RepositoryInterface(stub_model)
        repo._initialized = True
        yield repo


@pytest_asyncio.fixture
def stub_repository_invalid_model():
    with patch.object(RepositoryInterface, "_initialize", return_value=None):
        stub_model = Mock(
            NAME='mock_model',
            model_validate=Mock(return_value=False),
        )
        repo = RepositoryInterface(stub_model)
        repo._initialized = True
        yield repo


@pytest.mark.asyncio
async def test_repository_exception_handler_no_exception():
    async def method(self, *args, **kwargs):  # pylint: disable=unused-argument
        return args, kwargs

    mock_kwargs = {'foo': 'bar'}
    mock_args = ('foo', 'bar')
    mock_repo = Mock(model=Mock(NAME='mock_model'))
    wrapped_method = repository_exception_handler(method)
    with patch('lib.repositories.interface.logger') as mock_logger:
        assert await wrapped_method(mock_repo, *mock_args, **mock_kwargs) == (
            mock_args,
            mock_kwargs,
        )
        mock_logger.error.assert_not_called()
        mock_logger.info.assert_called_once_with(
            f"Call to repositories.{mock_repo.model.NAME}.{method.__name__} completed for {mock_kwargs}"
        )


@pytest.mark.asyncio
async def test_repository_exception_handler_db_exception():
    async def method(self, *args, **kwargs):
        raise PyMongoError

    wrapped_method = repository_exception_handler(method)
    with pytest.raises(PyMongoError):
        await wrapped_method(Mock(model=Mock(NAME='mock_model')))


@pytest.mark.asyncio
async def test_repository_exception_not_initialized_exception():
    async def method(self, *args, **kwargs):
        raise RepositoryNotInitializedException

    wrapped_method = repository_exception_handler(method)
    with pytest.raises(HTTPException) as exc:
        await wrapped_method(Mock(model=Mock(NAME='mock_model')))
    assert exc.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert (
        exc.value.detail
        == "Repository not initialized. Please try again later."
    )


@pytest.mark.asyncio
async def test_repository_exception_handler_unexpected_exception():
    async def method(self, *args, **kwargs):
        raise Exception  # pylint: disable=broad-exception-raised

    wrapped_method = repository_exception_handler(method)
    with pytest.raises(HTTPException) as exc:
        await wrapped_method(Mock(model=Mock(NAME='mock_model')))
    assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc.value.detail == 'Unexpected error ocurred'


@pytest.mark.asyncio
async def test_repository_interface_init(stub_repository):
    assert stub_repository.model.NAME == 'mock_model'


def test_get_model_repo(stub_repository):
    with patch(
        'lib.repositories.interface.importlib.import_module'
    ) as mock_import_module:
        mock_import_module.return_value = Mock(MockmodelRepository='mock_repo')
        assert (
            stub_repository.get_model_repo(Mock(NAME='mockmodel'))
            == 'mock_repo'
        )


@pytest.mark.asyncio
async def test_repository_insert_data(stub_repository, mock_db_interface):
    with patch(
        'lib.repositories.interface.RepositoryInterface.get_collection',
        return_value=mock_db_interface,
    ):
        assert await stub_repository.insert('mock_data') == 'mock_id'
        mock_db_interface.insert_one.assert_called_once_with('mock_data')


@pytest.mark.asyncio
async def test_repository_insert_invalid_data(stub_repository_invalid_model):
    with patch(
        'lib.repositories.interface.RepositoryInterface.get_collection',
        return_value=mock_db_interface,
    ):
        with pytest.raises(HTTPException):
            await stub_repository_invalid_model.insert('invalid_model_data')


@pytest.mark.asyncio
async def test_repository_update_data(stub_repository, mock_db_interface):
    with patch(
        'lib.repositories.interface.RepositoryInterface.get_collection',
        return_value=mock_db_interface,
    ):
        with patch(
            'lib.repositories.interface.ObjectId', side_effect=lambda x: x
        ):
            assert (
                await stub_repository.update_by_id(
                    'mock_data', data_id='mock_id'
                )
                is stub_repository
            )
            mock_db_interface.update_one.assert_called_once_with(
                {'_id': 'mock_id'}, {'$set': 'mock_data'}
            )


@pytest.mark.asyncio
async def test_repository_update_invalid_data(stub_repository_invalid_model):
    with patch(
        'lib.repositories.interface.RepositoryInterface.get_collection',
        return_value=mock_db_interface,
    ):
        with pytest.raises(HTTPException):
            await stub_repository_invalid_model.update_by_id(
                data_id='mock_id', data='invalid_model_data'
            )


@pytest.mark.asyncio
async def test_repository_find_data_found(
    stub_repository, mock_db_interface, stub_loaded_model
):
    with patch(
        'lib.repositories.interface.RepositoryInterface.get_collection',
        return_value=mock_db_interface,
    ):
        with patch(
            'lib.repositories.interface.ObjectId', side_effect=lambda x: x
        ):
            assert (
                await stub_repository.find_by_id(data_id='mock_id')
                == stub_repository.model.model_validate.return_value
            )
            mock_db_interface.find_one.assert_called_once_with(
                {'_id': 'mock_id'}
            )
            stub_repository.model.model_validate.return_value.set_id.assert_called_once_with(
                stub_loaded_model['_id']
            )


@pytest.mark.asyncio
async def test_repository_find_data_not_found(
    stub_repository, mock_db_interface
):
    mock_db_interface.find_one.return_value = None
    with patch(
        'lib.repositories.interface.RepositoryInterface.get_collection',
        return_value=mock_db_interface,
    ):
        with patch(
            'lib.repositories.interface.ObjectId', side_effect=lambda x: x
        ):
            assert await stub_repository.find_by_id(data_id='mock_id') is None
            mock_db_interface.find_one.assert_called_once_with(
                {'_id': 'mock_id'}
            )


@pytest.mark.asyncio
async def test_repository_delete_data(stub_repository, mock_db_interface):
    with patch(
        'lib.repositories.interface.RepositoryInterface.get_collection',
        return_value=mock_db_interface,
    ):
        with patch(
            'lib.repositories.interface.ObjectId', side_effect=lambda x: x
        ):
            assert (
                await stub_repository.delete_by_id(data_id='mock_id')
                is stub_repository
            )
            mock_db_interface.delete_one.assert_called_once_with(
                {'_id': 'mock_id'}
            )


@pytest.mark.asyncio
async def test_repository_find_by_query_found(
    stub_repository, mock_db_interface, stub_loaded_model
):
    with patch(
        'lib.repositories.interface.RepositoryInterface.get_collection',
        return_value=mock_db_interface,
    ):
        assert await stub_repository.find_by_query('mock_query') == [
            stub_repository.model.model_validate.return_value,
            stub_repository.model.model_validate.return_value,
        ]
        mock_db_interface.find.assert_called_once_with('mock_query')
        stub_repository.model.model_validate.return_value.set_id.assert_called_with(
            stub_loaded_model['_id']
        )


@pytest.mark.asyncio
async def test_repository_find_by_query_not_found(
    stub_repository, mock_db_interface_empty_find
):
    with patch(
        'lib.repositories.interface.RepositoryInterface.get_collection',
        return_value=mock_db_interface_empty_find,
    ):
        assert await stub_repository.find_by_query('mock_query') == []
        mock_db_interface_empty_find.find.assert_called_once_with('mock_query')
