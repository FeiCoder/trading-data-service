# Trading Data Service - MCP 接口文档 (Agent Tools)

本项目通过 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 将数据能力封装为智能体可以直接使用的“工具”。

## 运行模式

### 1. Stdio 模式 (管道)
通过宿主机命令或 `docker exec` 调用，适合 Claude Desktop 等本地客户端。
- **Command**: `python -m data_service.mcp_server`
- **MCP_MODE**: `stdio` (默认)

### 2. SSE 模式 (网络)
作为独立服务运行，适合跨容器或远程 Agent 调用。
- **Endpoint**: `http://localhost:8002/sse`
- **MCP_MODE**: `sse`

---

## 🛠️ 可用工具 (Tools)

### 1. `list_stocks`
获取市场内的股票清单。
- **Arguments**:
  - `market` (string): 市场 (CN/HK/US)。
- **用途**: 智能体用于了解特定市场有哪些可用标的。

### 2. `search_stock`
通过名称或代码定位股票。
- **Arguments**:
  - `keyword` (string): 关键词（如 "平安"）。
  - `market` (string): 市场。
- **用途**: 将自然语言指令（如“查看万科的行情”）转化为具体的代码。

### 3. `get_history`
获取 OHLCV 历史原始数据。
- **Arguments**:
  - `symbol` (string): 股票代码。
  - `days` (integer): 回溯天数。
- **用途**: 供智能体进行原始数据分析或自定义计算。

### 4. `analyze_technical`
一键获取全量技术指标。
- **Arguments**:
  - `symbol` (string): 股票代码。
  - `indicators` (string): 需要计算的指标名，如 "ma,macd"。
  - `days` (integer): 计算窗口所需数据量。
- **用途**: 核心工具。智能体通过此工具直接获得“超买/超卖”、“趋势强弱”等量化结论。

### 5. `get_finance_news`
获取财经新闻原始数据（不做 AI 分析）。
- **Arguments**:
  - `source` (string): 新闻源，支持 `all` / `sina` / `cls_hot` / `wallstreetcn` / `yahoo_rss`。
  - `limit` (integer): 返回条数。
  - `start_datetime` (string, optional): 开始时间（ISO 8601），用于历史新闻按时间过滤。
  - `end_datetime` (string, optional): 结束时间（ISO 8601），用于历史新闻按时间过滤。
- **用途**: 直接获取新浪财经、财联社热门、华尔街见闻、Yahoo Finance RSS 的原始新闻。

---

## 💡 Agent 开发建议

- **认证处理**: 在 Docker 部署时，请在 `mcp-server` 容器的 ENV 中设置 `AUTH_API_KEY`。智能体无需在对话中处理 Token。
- **上下文管理**: 尽量使用 `analyze_technical` 而不是 `get_history`，因为前者的返回结果经过了聚合，更节省智能体的输入 Token，且更容易让模型理解当前市场状态。
