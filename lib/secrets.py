from dotenv import dotenv_values
from pydantic import BaseModel

class Secrets(BaseModel):
    secrets: dict = dotenv_values(".env")

    def get_secret(self, key):
        return self.secrets[key]

# global instance
secrets_instance = Secrets()
