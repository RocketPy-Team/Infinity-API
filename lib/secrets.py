from dotenv import dotenv_values
from pydantic import BaseModel

class Secrets(BaseModel):
    """
        Secrets class to load secrets from .env file
    """
    secrets: dict = dotenv_values(".env")

    def get_secret(self, key):
        return self.secrets[key]

# global instance
secrets_instance = Secrets()
