"""
财经新闻数据服务
提供新浪财经、财联社热门、华尔街见闻原始新闻获取能力（不做 AI 分析）。
"""

import asyncio
import json
import logging
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Dict, List, Optional

from data_service.config import settings
from data_service.db import get_mongo_db
from data_service.layers.cache import get_cache_layer

logger = logging.getLogger(__name__)

_SUPPORTED_SOURCES = {"sina", "cls_hot", "wallstreetcn", "yahoo_rss", "all"}
_NEWS_HISTORY_CACHE_NS = "news_history"


def _pick_first(row: Dict[str, Any], keys: List[str]) -> str:
    for key in keys:
        value = row.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


class NewsService:
    def __init__(self):
        self._cache = get_cache_layer()

    async def get_news(
        self,
        source: str = "all",
        limit: int = 20,
        start_datetime: Optional[str] = None,
        end_datetime: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        source = source.lower()
        if source not in _SUPPORTED_SOURCES:
            raise ValueError(f"不支持的新闻源: {source}")

        if start_datetime or end_datetime:
            start_dt = self._parse_datetime(start_datetime) if start_datetime else None
            end_dt = self._parse_datetime(end_datetime) if end_datetime else None
            if start_datetime and start_dt is None:
                raise ValueError("开始时间格式无效，需使用 ISO 8601 或 RFC 822")
            if end_datetime and end_dt is None:
                raise ValueError("结束时间格式无效，需使用 ISO 8601 或 RFC 822")
            if start_dt and end_dt and start_dt > end_dt:
                raise ValueError("开始时间不能晚于结束时间")

            cache_key_start = start_dt.isoformat() if start_dt else ""
            cache_key_end = end_dt.isoformat() if end_dt else ""
            cached = await self._cache.get(_NEWS_HISTORY_CACHE_NS, source, cache_key_start, cache_key_end, str(limit))
            if cached is not None:
                return cached

            filtered = self._filter_news_by_datetime(await self._fetch_news(source, limit), start_dt, end_dt)[:limit]
            await self._cache.set(filtered, _NEWS_HISTORY_CACHE_NS, source, cache_key_start, cache_key_end, str(limit), ttl=settings.NEWS_CACHE_TTL)
            return filtered

        return (await self._fetch_news(source, limit))[:limit]

    async def _fetch_news(self, source: str, limit: int) -> List[Dict[str, Any]]:
        if source == "sina":
            return await self._fetch_sina_news(limit)
        if source == "cls_hot":
            return await self._fetch_cls_hot_news(limit)
        if source == "wallstreetcn":
            return await self._fetch_wallstreetcn_news(limit)
        if source == "yahoo_rss":
            return await self._fetch_yahoo_rss_news(limit)

        return (
            await self._fetch_sina_news(limit)
            + await self._fetch_cls_hot_news(limit)
            + await self._fetch_wallstreetcn_news(limit)
            + await self._fetch_yahoo_rss_news(limit)
        )

    def _parse_datetime(self, value: Optional[str]) -> Optional[datetime]:
        if value is None:
            return None

        text = str(value).strip()
        if not text:
            return None
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"

        try:
            dt = datetime.fromisoformat(text)
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except Exception:
            pass

        try:
            dt = parsedate_to_datetime(text)
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except Exception:
            return None

    def _filter_news_by_datetime(
        self,
        rows: List[Dict[str, Any]],
        start_dt: Optional[datetime],
        end_dt: Optional[datetime],
    ) -> List[Dict[str, Any]]:
        if start_dt is None and end_dt is None:
            return rows

        filtered = []
        for row in rows:
            published_dt = self._parse_datetime(str(row.get("published_at", "")).strip())
            if published_dt is None:
                continue
            if start_dt and published_dt < start_dt:
                continue
            if end_dt and published_dt > end_dt:
                continue
            filtered.append(row)
        return filtered

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
            resource = item.get("resource") or {}
            rows.append(
                {
                    "source": "wallstreetcn",
                    "title": str(resource.get("title", "")).strip(),
                    "content": str(resource.get("content_short", "")).strip(),
                    "published_at": str(datetime.fromtimestamp(resource.get("display_time", 0), tz=timezone.utc).isoformat()) if resource.get("display_time") else "",
                    "url": str(resource.get("uri", "")).strip(),
                }
            )
        return rows

    async def _fetch_yahoo_rss_news(self, limit: int) -> List[Dict[str, Any]]:
        def _fetch():
            req = urllib.request.Request(
                "https://finance.yahoo.com/news/rssindex",
                headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            )
            with urllib.request.urlopen(req, timeout=8) as response:
                return ET.fromstring(response.read())

        root = await self._run_with_timeout(_fetch)
        if root is None:
            return []

        rows = []
        for item in root.findall("./channel/item")[:limit]:
            rows.append(
                {
                    "source": "yahoo_rss",
                    "title": (item.findtext("title") or "").strip(),
                    "content": (item.findtext("description") or "").strip(),
                    "published_at": (item.findtext("pubDate") or "").strip(),
                    "url": (item.findtext("link") or "").strip(),
                }
            )
        return rows

    async def save_news_to_db(self, news_list: List[Dict[str, Any]]):
        """将新闻持久化到 MongoDB，避免重复"""
        db = get_mongo_db()
        if db is None or not news_list:
            return

        collection = db["news_history"]
        # 创建索引以加速去重和时间查询
        await collection.create_index([("url", 1)], unique=True)
        await collection.create_index([("published_at", -1)])

        count = 0
        for item in news_list:
            if not item.get("url"):
                continue
            try:
                # 使用 upsert 逻辑，以 URL 作为唯一标识
                await collection.update_one(
                    {"url": item["url"]},
                    {"$set": item},
                    upsert=True
                )
                count += 1
            except Exception as e:
                logger.error(f"持久化新闻失败: {e}")
        
        if count > 0:
            logger.info(f"已持久化 {count} 条新闻到数据库")


_news_service: Optional[NewsService] = None


def get_news_service() -> NewsService:
    global _news_service
    if _news_service is None:
        _news_service = NewsService()
    return _news_service
