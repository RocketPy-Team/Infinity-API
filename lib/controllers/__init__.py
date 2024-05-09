# lib/controllers/__init__.py


def parse_error(error):
    exc_type = type(error).__name__
    exc_obj = f"{error}".replace("\n", " ").replace("   ", " ")
    return f"{exc_type} exception: {exc_obj}"
