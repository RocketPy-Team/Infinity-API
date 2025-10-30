from unittest.mock import MagicMock, patch

import pytest

from src.api import app
from src.mcp.server import build_mcp


@pytest.fixture(autouse=True)
def reset_mcp_state():
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
