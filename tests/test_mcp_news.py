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


@pytest.mark.asyncio
async def test_get_finance_news_tool_yahoo_rss():
    mock_service = AsyncMock()
    mock_service.get_news.return_value = [{"source": "yahoo_rss", "title": "yahoo"}]
    with patch("data_service.mcp_server.get_news_service", return_value=mock_service):
        result = await mcp_server.get_finance_news(source="yahoo_rss", limit=1)

    assert len(result) == 1
    assert result[0]["source"] == "yahoo_rss"


@pytest.mark.asyncio
async def test_get_finance_news_tool_with_datetime():
    mock_service = AsyncMock()
    mock_service.get_news.return_value = [{"source": "yahoo_rss", "title": "history"}]
    with patch("data_service.mcp_server.get_news_service", return_value=mock_service):
        result = await mcp_server.get_finance_news(
            source="yahoo_rss",
            limit=1,
            start_datetime="2026-02-28T09:00:00+00:00",
            end_datetime="2026-02-28T11:00:00+00:00",
        )

    assert len(result) == 1
    mock_service.get_news.assert_awaited_once_with(
        source="yahoo_rss",
        limit=1,
        start_datetime="2026-02-28T09:00:00+00:00",
        end_datetime="2026-02-28T11:00:00+00:00",
    )
