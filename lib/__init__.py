# lib/__init__.py
import logging

logging.basicConfig(
    level=logging.INFO,
    filename='app.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
)


def parse_error(error):
    exc_type = type(error).__name__
    exc_obj = f"{error}".replace("\n", " ").replace("   ", " ")
    return f"{exc_type} exception: {exc_obj}"


from .api import app  # noqa
