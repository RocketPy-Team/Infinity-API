from dotenv import dotenv_values

class Secrets:
    def __init__(self):
        secrets = dotenv_values(".env")

    def get_secret(self, key):
        return self.secrets[key]

# global instance
secrets_instance = Secrets()
