"""FastMCP integration helpers for Infinity API."""

from __future__ import annotations

from fastapi import FastAPI
from fastmcp import FastMCP, settings


def build_mcp(app: FastAPI) -> FastMCP:
    """
    Create (or return cached) FastMCP server
    that mirrors the FastAPI app.
    """

    if hasattr(app.state, 'mcp'):
        return app.state.mcp  # type: ignore[attr-defined]

    settings.experimental.enable_new_openapi_parser = True
    mcp = FastMCP.from_fastapi(app, name=app.title)
    app.state.mcp = mcp  # type: ignore[attr-defined]
    return mcp
