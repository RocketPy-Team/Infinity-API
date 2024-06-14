"""
This is the main API file for the RocketPy API.
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import RedirectResponse, JSONResponse

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

from lib import logger, parse_error
from lib.routes import flight, environment, motor, rocket

app = FastAPI(
    swagger_ui_parameters={
        "defaultModelsExpandDepth": 0,
        "syntaxHighlight.theme": "obsidian",
    }
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(flight.router)
app.include_router(environment.router)
app.include_router(motor.router)
app.include_router(rocket.router)

FastAPIInstrumentor.instrument_app(app)
RequestsInstrumentor().instrument()

# Compress responses above 1KB
app.add_middleware(GZipMiddleware, minimum_size=1000)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="RocketPy Infinity-API",
        version="1.2.2 BETA",
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
            "<p>Currently, the API only supports TrapezoidalFins. We apologize for the limitation, but we are actively working to expand its capabilities soon.</p>"
            "<p>Please report any bugs at <a href='https://github.com/RocketPy-Team/infinity-api/issues/new/choose' style='text-decoration: none; color: #008CBA;'>GitHub Issues</a></p>"
        ),
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://raw.githubusercontent.com/RocketPy-Team/RocketPy/master/docs/static/RocketPy_Logo_black.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Main
@app.get("/", include_in_schema=False)
async def main_page():
    """
    Redirects to API docs.
    """
    return RedirectResponse(url="/redoc")


# Additional routes
@app.get("/health", status_code=status.HTTP_200_OK, include_in_schema=False)
async def __perform_healthcheck():
    return {"health": "Everything OK!"}


# Errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    exc_str = parse_error(exc)
    logger.error(f"{request}: {exc_str}")
    return JSONResponse(
        content=exc_str, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )
