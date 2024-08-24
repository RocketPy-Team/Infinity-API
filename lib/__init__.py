# lib/__init__.py
import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Creates log handlers
file_handler = logging.FileHandler("app.log")
stdout_handler = logging.StreamHandler(sys.stdout)

# Creates log formatter and add it to handlers
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
stdout_handler.setFormatter(formatter)

if not logger.hasHandlers():
    logger.addHandler(file_handler)
    logger.addHandler(stdout_handler)


def parse_error(error):
    exc_type = type(error).__name__
    exc_obj = f"{error}".replace("\n", " ").replace("   ", " ")
    return f"{exc_type}: {exc_obj}"


from lib.api import app
