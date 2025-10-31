from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastmcp.client import Client
from fastapi.routing import APIRoute

from src.api import app, rest_app
from src.mcp.server import build_mcp


@pytest.fixture(autouse=True)
def reset_mcp_state():
    """
    Ensure the FastAPI app has no lingering MCP state before and after a test.
    
    This fixture deletes app.state.mcp if it exists, yields control to the test, and then deletes app.state.mcp again to guarantee the MCP state is cleared between tests.
    """
    if hasattr(rest_app.state, 'mcp'):
        delattr(rest_app.state, 'mcp')
    yield
    if hasattr(rest_app.state, 'mcp'):
        delattr(rest_app.state, 'mcp')


def test_build_mcp_uses_fastapi_adapter():
    mock_mcp = MagicMock()
    with patch(
        'src.mcp.server.FastMCP.from_fastapi', return_value=mock_mcp
    ) as mock_factory:
        result = build_mcp(rest_app)
        assert result is mock_mcp
        mock_factory.assert_called_once_with(rest_app, name=rest_app.title)
        again = build_mcp(rest_app)
        assert again is mock_mcp
        mock_factory.assert_called_once()


@pytest.mark.asyncio
async def test_mcp_tools_cover_registered_routes():
    mcp_server = build_mcp(rest_app)

    async with Client(mcp_server) as client:
        tools = await client.list_tools()

    tool_by_name = {tool.name: tool for tool in tools}

    expected = {}
    for route in rest_app.routes:
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
        assert path_params.issubset(
            required
        ), f"{tool_name} missing path params {path_params - required}"


@pytest.mark.asyncio
async def test_combined_app_serves_rest_and_mcp(monkeypatch):
    monkeypatch.setattr('src.mcp.server.FastMCP.from_fastapi', MagicMock())
    build_mcp(rest_app)

    from httpx import ASGITransport, AsyncClient

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url='http://test'
    ) as client:
        resp_rest = await client.get('/health')
        assert resp_rest.status_code == 200
        resp_docs = await client.get('/docs')
        assert resp_docs.status_code == 200