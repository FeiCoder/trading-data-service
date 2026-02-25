"""
TradingAgents-CN MCP Server
基于 Model Context Protocol (MCP) 封装，方便 Claude/GPT 智能体直接调用工具。
"""

import os
from typing import Optional, List
from datetime import date, timedelta

from fastmcp import FastMCP
from data_service.services.stock_service import get_stock_service
from data_service.services.technical_service import get_technical_service
from data_service.config import settings

# 初始化 FastMCP
mcp = FastMCP("StockTrading")

@mcp.tool()
async def list_stocks(market: str = "CN"):
    """
    获取指定市场的全部股票代码和名称。
    :param market: 市场代码，如 'CN' (A股), 'HK' (港股), 'US' (美股)。
    """
    svc = get_stock_service()
    stocks = await svc.get_stock_list(market=market)
    # 抽取关键信息，避免返回体积过大
    return [{"symbol": s["symbol"], "name": s["name"]} for s in stocks[:2000]]

@mcp.tool()
async def search_stock(keyword: str, market: str = "CN"):
    """
    通过名称或代码搜索股票信息。
    :param keyword: 关键词（如 '平安' 或 '000001'）。
    :param market: 市场代码。
    """
    svc = get_stock_service()
    return await svc.search_stocks(keyword, market=market)

@mcp.tool()
async def get_history(symbol: str, days: int = 30, market: str = "CN"):
    """
    获取股票历史 K 线数据（OHLCV）。
    :param symbol: 股票代码（如 '000001'）。
    :param days: 获取最近多少天的数据（默认 30）。
    :param market: 市场代码。
    """
    svc = get_stock_service()
    end_date = date.today().isoformat()
    start_date = (date.today() - timedelta(days=days)).isoformat()
    
    data = await svc.get_stock_history(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        market=market
    )
    return data

@mcp.tool()
async def analyze_technical(symbol: str, indicators: str = "ma,macd,rsi", days: int = 90):
    """
    获取股票的技术指标分析结果（含最新状态和历史趋势）。
    :param symbol: 股票代码。
    :param indicators: 想要计算的指标，逗号分隔，支持: ma,macd,rsi,boll,kdj,atr。
    :param days: 回溯计算所需的数据周期。
    """
    svc = get_technical_service()
    end_date = date.today().isoformat()
    start_date = (date.today() - timedelta(days=days)).isoformat()
    
    indicator_list = [i.strip() for i in indicators.split(",")]
    return await svc.get_indicators(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        indicators=indicator_list
    )

if __name__ == "__main__":
    # 该文件既可以作为 stdio 服务器运行 (默认)，也可以作为 SSE 服务器运行
    # 通过环境变量 MCP_MODE=sse 切换，适合跨容器或远程调用
    mode = os.getenv("MCP_MODE", "stdio").lower()
    
    if mode == "sse":
        port = int(os.getenv("MCP_PORT", "8002"))
        print(f"🚀 Starting MCP SSE Server on port {port}...")
        mcp.run(transport="sse", host="0.0.0.0", port=port)
    else:
        # stdio 模式，适合本地 Claude Desktop 或 docker exec 调用
        mcp.run(transport="stdio")
