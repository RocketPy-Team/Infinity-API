from __future__ import annotations

import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, RedirectResponse

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

from src import logger, parse_error
from src.mcp.server import build_mcp
from src.routes import environment, flight, motor, rocket
from src.utils import RocketPyGZipMiddleware

log = logging.getLogger(__name__)


# --- REST application -------------------------------------------------------

rest_app = FastAPI(
    title="Infinity API",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": 0,
        "syntaxHighlight.theme": "obsidian",
    },
)

rest_app.include_router(flight.router)
rest_app.include_router(environment.router)
rest_app.include_router(motor.router)
rest_app.include_router(rocket.router)

FastAPIInstrumentor.instrument_app(rest_app)
RequestsInstrumentor().instrument()

# Compress responses above 1KB
rest_app.add_middleware(RocketPyGZipMiddleware, minimum_size=1000)


def custom_openapi():
    if rest_app.openapi_schema:
        return rest_app.openapi_schema
    openapi_schema = get_openapi(
        title="RocketPy Infinity-API",
        version="3.0.0",
        description=(
            "<p style='font-size: 18px;'>RocketPy Infinity-API is a RESTful Open API for RocketPy, a rocket flight simulator.</p>"
            "<br/>"
            "<button style='background-color: #4CAF50; color: white; border: none; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer;'>"
            "<a href='https://api.rocketpy.org/docs' style='color: white; text-decoration: none;'>Swagger UI</a>"
            "</button>"
            "<br/>"
            "<button style='background-color: #008CBA; color: white; border: none; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer;'>"
            "<a href='https://api.rocketpy.org/redoc' style='color: white; text-decoration: none;'>ReDoc</a>"
            "</button>"
            "<p>Create, manage, and simulate rocket flights, environments, rockets, and motors.</p>"
            "<p>Please report any bugs at <a href='https://github.com/RocketPy-Team/infinity-api/issues/new/choose' style='text-decoration: none; color: #008CBA;'>GitHub Issues</a></p>"
        ),
        routes=rest_app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://raw.githubusercontent.com/RocketPy-Team/RocketPy/master/docs/static/RocketPy_Logo_black.png"
    }
    rest_app.openapi_schema = openapi_schema
    return rest_app.openapi_schema


rest_app.openapi = custom_openapi


# Main
@rest_app.get("/", include_in_schema=False)
async def main_page():
    """Redirect to API docs."""
    return RedirectResponse(url="/redoc")


# Additional routes
@rest_app.get(
    "/health", status_code=status.HTTP_200_OK, include_in_schema=False
)
async def __perform_healthcheck():
    return {"health": "Everything OK!"}


# Global exception handler
@rest_app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    exc_str = parse_error(exc)
    logger.error("%s: %s", request, exc_str)
    return JSONResponse(
        content=exc_str, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


# --- MCP server mounted under /mcp ------------------------------------------
mcp_app = build_mcp(rest_app).http_app(path="/")


def _combine_lifespans(rest_lifespan, mcp_lifespan):
    """Combine FastAPI and MCP lifespans."""

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        async with rest_lifespan(app):
            async with mcp_lifespan(app):
                yield

    return lifespan


app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=_combine_lifespans(
        rest_app.router.lifespan_context, mcp_app.lifespan
    ),
)
app.mount("/mcp", mcp_app)
app.mount("/", rest_app)

__all__ = ["app", "rest_app"]
