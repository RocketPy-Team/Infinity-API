# lib/controllers/__init__.py


def parse_error(e):
    exc_str = f"{e}".replace("\n", " ").replace("   ", " ")
    return exc_str
