---
name: stock-query
description: 提供了获取股票列表、搜索股票以及查询股票历史K线数据（OHLCV）的能力。
---

# 股票数据查询 (Stock Query)

本 Skill 用于从 `trading-data-service` 获取多市场的股票基础信息和历史交易数据。

## 核心功能

1.  **获取股票列表**：按市场（CN/HK/US）获取完整的股票清单。
2.  **搜索股票**：根据关键词（代码或名称）在指定市场中搜索股票。
3.  **查询历史K线**：获取指定股票在特定日期范围内的标准化 OHLCV 数据（开盘、最高、最低、收盘、成交量等）。

## 接口规范

所有的请求都需要在 Header 中包含 JWT Token: `Authorization: Bearer <TOKEN>`。

### 1. 获取股票列表
- **路径**: `GET /api/stocks/list`
- **参数**:
    - `market` (string): 市场代码 (CN, HK, US)，默认 `CN`。
    - `force_refresh` (boolean): 是否强制刷新缓存，默认 `false`。

### 2. 搜索股票
- **路径**: `GET /api/stocks/search`
- **参数**:
    - `keyword` (string, 必填): 搜索关键词（代码或名称）。
    - `market` (string): 市场代码，默认 `CN`。

### 3. 获取历史 K 线
- **路径**: `GET /api/stocks/{symbol}/history`
- **参数**:
    - `symbol` (path, string): 股票代码（例如 `000001`）。
    - `start_date` (query, string): 开始日期 (YYYY-MM-DD)。
    - `end_date` (query, string): 结束日期 (YYYY-MM-DD)。
    - `market` (query, string): 市场，默认 `CN`。

## 使用建议

- 进行策略回测或分析前，应先通过 `search` 确认股票代码。
- 由于 A 股数据源（AKShare）可能存在频率限制，系统内部实现了三级缓存（Redis -> MongoDB -> 文件），建议尽量利用缓存。
- 在请求 `search` 时，如果涉及中文关键词，请务必进行 URL 编码。

## 示例

```bash
# 搜索“平安”
curl -G "http://localhost:8001/api/stocks/search" --data-urlencode "keyword=平安" -H "Authorization: Bearer $TOKEN"

# 获取万科 A 的 2024 年第一季度历史数据
curl "http://localhost:8001/api/stocks/000002/history?start_date=2024-01-01&end_date=2024-03-31" -H "Authorization: Bearer $TOKEN"
```
