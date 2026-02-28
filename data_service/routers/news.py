"""
财经新闻路由
GET /api/news - 获取财经新闻原始数据（新浪财经 / 财联社热门 / 华尔街见闻）
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from data_service.models.response import ApiResponse
from data_service.routers.auth import get_current_user
from data_service.services.news_service import get_news_service

router = APIRouter(prefix="/api/news", tags=["财经新闻"])


@router.get("", response_model=ApiResponse)
async def get_news(
    source: str = Query(default="all", description="新闻源: all / sina / cls_hot / wallstreetcn"),
    limit: int = Query(default=20, ge=1, le=100, description="返回条数"),
    current_user: dict = Depends(get_current_user),
):
    svc = get_news_service()
    try:
        news = await svc.get_news(source=source, limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    return ApiResponse.ok(
        data={"source": source, "count": len(news), "news": news},
        message="获取财经新闻成功",
    )
