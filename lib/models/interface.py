from typing import Self, Optional
from abc import abstractmethod, ABC
from pydantic import BaseModel, PrivateAttr, ConfigDict
from bson import ObjectId


class ApiBaseModel(BaseModel, ABC):
    _id: Optional[ObjectId] = PrivateAttr(default=None)
    model_config = ConfigDict(
        json_encoders={ObjectId: str},
        use_enum_values=True,
        validate_default=True,
        validate_all_in_root=True,
        validate_assignment=True,
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
