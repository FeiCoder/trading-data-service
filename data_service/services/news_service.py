"""
财经新闻数据服务
提供新浪财经、财联社热门、华尔街见闻原始新闻获取能力（不做 AI 分析）。
"""

import asyncio
import json
import logging
import urllib.request
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_SUPPORTED_SOURCES = {"sina", "cls_hot", "wallstreetcn", "all"}


def _pick_first(row: Dict[str, Any], keys: List[str]) -> str:
    for key in keys:
        value = row.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


class NewsService:
    async def get_news(self, source: str = "all", limit: int = 20) -> List[Dict[str, Any]]:
        source = source.lower()
        if source not in _SUPPORTED_SOURCES:
            raise ValueError(f"不支持的新闻源: {source}")

        if source == "sina":
            return (await self._fetch_sina_news(limit))[:limit]
        if source == "cls_hot":
            return (await self._fetch_cls_hot_news(limit))[:limit]
        if source == "wallstreetcn":
            return (await self._fetch_wallstreetcn_news(limit))[:limit]

        merged = (
            await self._fetch_sina_news(limit)
            + await self._fetch_cls_hot_news(limit)
            + await self._fetch_wallstreetcn_news(limit)
        )
        return merged[:limit]

    async def _run_with_timeout(self, func, timeout: float = 8.0):
        try:
            return await asyncio.wait_for(asyncio.to_thread(func), timeout=timeout)
        except Exception as exc:
            logger.warning(f"新闻抓取失败: {exc}")
            return None

    async def _fetch_sina_news(self, limit: int) -> List[Dict[str, Any]]:
        def _fetch():
            import akshare as ak

            return ak.stock_info_global_sina()

        df = await self._run_with_timeout(_fetch)
        if df is None or df.empty:
            return []
        rows = []
        for row in df.to_dict("records")[:limit]:
            rows.append(
                {
                    "source": "sina",
                    "title": _pick_first(row, ["标题", "title", "内容", "content"]),
                    "content": _pick_first(row, ["内容", "content", "摘要"]),
                    "published_at": _pick_first(row, ["发布时间", "时间", "date", "datetime"]),
                    "url": _pick_first(row, ["链接", "link", "url"]),
                }
            )
        return rows

    async def _fetch_cls_hot_news(self, limit: int) -> List[Dict[str, Any]]:
        def _fetch():
            import akshare as ak

            return ak.stock_info_global_cls()

        df = await self._run_with_timeout(_fetch)
        if df is None or df.empty:
            return []
        rows = []
        for row in df.to_dict("records")[:limit]:
            rows.append(
                {
                    "source": "cls_hot",
                    "title": _pick_first(row, ["标题", "title", "内容", "content"]),
                    "content": _pick_first(row, ["内容", "content", "摘要"]),
                    "published_at": _pick_first(row, ["发布时间", "时间", "date", "datetime"]),
                    "url": _pick_first(row, ["链接", "link", "url"]),
                }
            )
        return rows

    async def _fetch_wallstreetcn_news(self, limit: int) -> List[Dict[str, Any]]:
        def _fetch():
            with urllib.request.urlopen(f"https://api-one-wscn.awtmt.com/apiv1/content/information-flow?channel=global-channel&limit={limit}", timeout=8) as response:
                return json.loads(response.read().decode("utf-8"))

        data = await self._run_with_timeout(_fetch)
        if not data:
            return []

        items = (((data or {}).get("data") or {}).get("items") or [])[:limit]
        rows = []
        for item in items:
            rows.append(
                {
                    "source": "wallstreetcn",
                    "title": str(item.get("title", "")).strip(),
                    "content": str(item.get("description", "")).strip(),
                    "published_at": str(item.get("display_time", "")).strip(),
                    "url": str(item.get("uri", "")).strip(),
                }
            )
        return rows


_news_service: Optional[NewsService] = None


def get_news_service() -> NewsService:
    global _news_service
    if _news_service is None:
        _news_service = NewsService()
    return _news_service
