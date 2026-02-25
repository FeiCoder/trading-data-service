# Trading Data Service Skills

一套为 AI 智能体（如 Claude, GPT-based Agents）设计的标准化 Skills，用于快速集成股票数据能力。

## 目录

- [stock-service-auth](./stock-service-auth/SKILL.md): 身份认证与 Token 管理。
- [stock-query](./stock-query/SKILL.md): 股票列表、搜索及历史 K 线获取。
- [technical-analysis](./technical-analysis/SKILL.md): 常用技术指标（MA, MACD, RSI 等）计算。

## 如何使用

1.  **加载 Skill**: 将对应的 `SKILL.md` 内容作为系统提示词的一部分或通过 Skill 加载机制载入智能体。
2.  **执行任务**: 智能体现在可以理解如何构造 API 请求来回答诸如“分析平安银行的趋势”或“获取今日 A 股清单”等问题。
3.  **遵循规范**: 确保智能体了解 base_url (默认 `http://localhost:8001`) 以及认证头部的要求。

## 开发意图

这些 Skills 将本项目的底层 API 抽象为高层指令集，使得智能体无需关心具体的 `akshare` 或 `pandas` 实现细节，只需通过标准 HTTP 交互即可构建复杂的量化策略决策链路。
