---
name: technical-analysis
description: 基于历史股价计算常用的量化技术指标，如移动平均线、MACD、RSI、布林带等。
---

# 技术指标分析 (Technical Analysis)

本 Skill 用于对指定股票的历史数据进行计算，返回标准化的量化技术指标，支持多种常用参数设置。

## 支持的指标列表

- **MA (Simple Moving Average)**: 简单移动平均线（默认周期：5, 10, 20, 60）。
- **EMA (Exponential Moving Average)**: 指数移动平均线。
- **MACD (Moving Average Convergence Divergence)**: 指数平滑异同移动平均线。
- **RSI (Relative Strength Index)**: 相对强弱指标。
- **BOLL (Bollinger Bands)**: 布林带。
- **KDJ**: 随机指标。
- **ATR (Average True Range)**: 平均真实波幅。

## 接口规范

- **路径**: `GET /api/technical/{symbol}`
- **Header**: `Authorization: Bearer <TOKEN>`
- **Query 参数**:
    - `symbol` (path): 股票代码。
    - `market`: 市场代码 (CN, HK, US)，默认 `CN`。
    - `start_date`: 计算开始日期 (YYYY-MM-DD)，建议包含足够的预热期（如计算 MA60 需至少提前 60 天的数据）。
    - `end_date`: 计算结束日期 (YYYY-MM-DD)。
    - `indicators`: 逗号分隔的指标名（如 `ma,macd,rsi`），不填则返回所有支持的指标。

## 输出格式

接口返回包含两个核心部分：
1.  **latest**: 最新一期的指标值摘要，适合实时决策。
2.  **history**: 包含历史每一天的 OHLCV 及对应的指标计算结果，适合绘制图表或深度序列分析。

## 使用建议

- 若仅需最新状态（如“当前是否超买”），可直接读取响应中的 `data.latest`。
- 如果需要自定义周期，可以通过 `indicators` 参数进行筛选，但这目前主要受限于后端 `AnalysisLayer` 的预设逻辑。
- 获取指标数据前，系统会自动获取并缓存底层 K 线数据。

## 示例

```bash
# 获取平安银行 (000001) 的 MA, MACD 和 RSI 详情
curl "http://localhost:8001/api/technical/000001?indicators=ma,macd,rsi" -H "Authorization: Bearer $TOKEN"
```
