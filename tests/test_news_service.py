from unittest.mock import AsyncMock, patch

import pytest

from data_service.services.news_service import NewsService


@pytest.mark.asyncio
async def test_get_news_yahoo_rss_parse():
    xml_text = """<?xml version="1.0"?>
<rss><channel>
  <item>
    <title>Yahoo Title</title>
    <description>Yahoo Desc</description>
    <link>https://finance.yahoo.com/news/example</link>
    <pubDate>Sat, 28 Feb 2026 10:00:00 GMT</pubDate>
  </item>
</channel></rss>
"""

    class _MockResp:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return xml_text.encode("utf-8")

    svc = NewsService()
    with patch("urllib.request.urlopen", return_value=_MockResp()):
        rows = await svc.get_news(source="yahoo_rss", limit=1)

    assert len(rows) == 1
    assert rows[0]["source"] == "yahoo_rss"
    assert rows[0]["title"] == "Yahoo Title"


@pytest.mark.asyncio
async def test_get_news_datetime_filter_with_cache():
    svc = NewsService()
    svc._cache.get = AsyncMock(return_value=None)
    svc._cache.set = AsyncMock()
    svc._fetch_yahoo_rss_news = AsyncMock(
        return_value=[
            {"source": "yahoo_rss", "title": "in", "published_at": "Sat, 28 Feb 2026 10:00:00 GMT", "url": ""},
            {"source": "yahoo_rss", "title": "out", "published_at": "Sat, 28 Feb 2026 08:00:00 GMT", "url": ""},
        ]
    )

    rows = await svc.get_news(
        source="yahoo_rss",
        limit=10,
        start_datetime="2026-02-28T09:00:00+00:00",
        end_datetime="2026-02-28T11:00:00+00:00",
    )

    assert [r["title"] for r in rows] == ["in"]
    svc._cache.set.assert_awaited()
