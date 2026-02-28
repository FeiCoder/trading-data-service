from unittest.mock import AsyncMock, patch

import pytest

from data_service import mcp_server


@pytest.mark.asyncio
async def test_get_finance_news_tool():
    mock_service = AsyncMock()
    mock_service.get_news.return_value = [{"source": "cls_hot", "title": "hot"}]
    with patch("data_service.mcp_server.get_news_service", return_value=mock_service):
        result = await mcp_server.get_finance_news(source="cls_hot", limit=1)

    assert len(result) == 1
    assert result[0]["source"] == "cls_hot"
