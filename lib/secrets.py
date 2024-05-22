import os
from dotenv import dotenv_values


class Secrets:
    """
    Secrets class to load secrets from .env file
    """

    secrets = dotenv_values(".env")

    @staticmethod
    def get_os_secret(key):
        return os.environ.get(key)

    @classmethod
    def get_secret(cls, key):
        dotenv_secret = cls.secrets.get(key)
        if not dotenv_secret:
            return cls.get_os_secret(key)
        return dotenv_secret
