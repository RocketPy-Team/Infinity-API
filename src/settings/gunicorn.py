import uptrace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from uvicorn.workers import UvicornWorker
from src.secrets import Secrets


def post_fork(server, worker):  # pylint: disable=unused-argument
    uptrace.configure_opentelemetry(
        dsn=Secrets.get_secret("UPTRACE_DSN"),
        service_name="infinity-api",
        service_version="2.2.0",
        deployment_environment="production",
    )
    from src.api import (  # pylint: disable=import-outside-toplevel
        app as fastapi_server,
    )

    FastAPIInstrumentor.instrument_app(fastapi_server)


class UvloopUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {"loop": "uvloop"}
