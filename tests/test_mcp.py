import asyncio
from data_service.mcp_server import mcp

async def test():
    # 测试搜索工具
    print("--- 正在测试搜索股票工具 ---")
    result = await mcp.call_tool("search_stock", {"keyword": "平安"})
    print(result)

    # 测试技术指标工具
    print("\n--- 正在测试技术指标工具 ---")
    result = await mcp.call_tool("analyze_technical", {"symbol": "000001", "indicators": "ma,rsi"})
    print(result)

if __name__ == "__main__":
    asyncio.run(test())