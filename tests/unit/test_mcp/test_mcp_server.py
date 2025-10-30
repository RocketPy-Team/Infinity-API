from __future__ import annotations


from unittest.mock import MagicMock, patch

import pytest

from fastmcp.client import Client
from fastapi.routing import APIRoute

from src.api import app
from src.mcp.server import build_mcp


@pytest.fixture(autouse=True)
def reset_mcp_state():
    """
    Ensure the FastAPI app has no lingering MCP state before and after a test.
    
    This fixture deletes app.state.mcp if it exists, yields control to the test, and then deletes app.state.mcp again to guarantee the MCP state is cleared between tests.
    """
    if hasattr(app.state, 'mcp'):
        delattr(app.state, 'mcp')
    yield
    if hasattr(app.state, 'mcp'):
        delattr(app.state, 'mcp')


def test_build_mcp_uses_fastapi_adapter():
    mock_mcp = MagicMock()
    with patch(
        'src.mcp.server.FastMCP.from_fastapi', return_value=mock_mcp
    ) as mock_factory:
        result = build_mcp(app)
        assert result is mock_mcp
        mock_factory.assert_called_once_with(app, name=app.title)
        # Subsequent calls reuse cached server
        again = build_mcp(app)
        assert again is mock_mcp
        mock_factory.assert_called_once()


@pytest.mark.asyncio
async def test_mcp_tools_cover_registered_routes():
    mcp_server = build_mcp(app)

    async with Client(mcp_server) as client:
        tools = await client.list_tools()

    tool_by_name = {tool.name: tool for tool in tools}

    expected = {}
    for route in app.routes:
        if not isinstance(route, APIRoute) or not route.include_in_schema:
            continue
        tag = route.tags[0].lower()
        tool_name = f"{route.name}_{tag}s"
        expected[tool_name] = route

    assert set(tool_by_name) == set(
        expected
    ), "Every FastAPI route should be exported as an MCP tool"

    for tool_name, route in expected.items():
        schema = tool_by_name[tool_name].inputSchema or {}
        required = set(schema.get('required', []))
        path_params = {param.name for param in route.dependant.path_params}
        # Path parameters must be represented as required MCP tool arguments
        assert path_params.issubset(
            required
        ), f"{tool_name} missing path params {path_params - required}"