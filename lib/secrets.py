import os
from dotenv import dotenv_values
from pydantic import BaseModel

class Secrets(BaseModel):
    """
        Secrets class to load secrets from .env file
    """
    secrets: dict = dotenv_values(".env")

    @staticmethod
    def get_os_secret(key):
        return os.environ.get(key)

    def get_secret(self, key):
        dotenv_secret = self.secrets.get(key)
        if not dotenv_secret:
            return self.get_os_secret(key)
        return dotenv_secret

# global instance
secrets_instance = Secrets()
