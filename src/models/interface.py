from typing import Self, Optional
from abc import abstractmethod, ABC
from pydantic import (
    BaseModel,
    PrivateAttr,
    ConfigDict,
)


class ApiBaseModel(BaseModel, ABC):
    """
    Base class for all models in the API.

    This class is used to define the common attributes and
    methods that all models in the API should have.
    """

    _id: Optional[str] = PrivateAttr(default=None)
    model_config = ConfigDict(
        use_enum_values=True,
        validate_default=True,
        validate_all_in_root=True,
        validate_assignment=True,
        ser_json_exclude_none=True,
    )

    def set_id(self, value):
        self._id = value

    def get_id(self):
        return self._id

    @property
    @abstractmethod
    def NAME():  # pylint: disable=invalid-name, no-method-argument
        pass

    @property
    @abstractmethod
    def METHODS():  # pylint: disable=invalid-name, no-method-argument
        pass

    @staticmethod
    @abstractmethod
    def UPDATED():  # pylint: disable=invalid-name
        pass

    @staticmethod
    @abstractmethod
    def DELETED():  # pylint: disable=invalid-name
        pass

    @staticmethod
    @abstractmethod
    def CREATED(model_id: str):  # pylint: disable=invalid-name
        pass

    @staticmethod
    @abstractmethod
    def RETRIEVED(model_instance: type(Self)):  # pylint: disable=invalid-name
        pass
