# trading-data-service

股票数据管理微服务 – 独立 HTTP API 服务。

本项目参考 [TradingAgents-CN](https://github.com/hsliuping/TradingAgents-CN) 项目实现。

提供股票数据管理、用户认证、多市场数据提供商、多级缓存和技术指标分析功能，支持通过 Docker 独立部署或加入现有容器网络协同运行。

## 功能特性

| 功能 | 说明 |
|------|------|
| 🔐 用户认证 | 基于 JWT 的无状态认证，用户信息可选存储于 MongoDB |
| 📊 股票数据 | A股 / 港股 / 美股历史 K 线及基础信息 |
| 🌐 多数据提供商 | AKShare（免费，默认）/ Tushare Pro / BaoStock / yfinance / FinnHub |
| 🗄️ 多级缓存 | Redis → MongoDB → 文件，自动降级，任何后端不可用均可运行 |
| 📈 技术指标 | MA / EMA / MACD / RSI / 布林带 / KDJ / ATR |
| 🐳 Docker 部署 | 容器网络内自动服务发现，支持连接外部 MongoDB / Redis |

## 分层架构

```
HTTP API Layer  (FastAPI)
      │
 Analysis Layer      ← MA / MACD / RSI / BOLL / KDJ / ATR
      │
Processing Layer     ← 数据清洗 / 格式化 / 标准化
      │
  Cache Layer        ← Redis (L1) → MongoDB (L2) → 文件 (L3)
      │
Acquisition Layer    ← AKShare / Tushare / BaoStock / yfinance
```

## 快速开始

### 本地开发

```bash
# 1. 安装依赖
pip install -e ".[dev]"
```
```bash
# 或采用uv方式：
uv sync
source .venv/bin/activate
```
```bash
# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，至少检查 JWT_SECRET 和数据库地址

# 3. 启动服务（无需外部数据库，自动降级为文件缓存）
uvicorn data_service.main:app --host 0.0.0.0 --port 8001 --reload

# 4. 访问 API 文档
open http://localhost:8001/docs
```

### Docker 一键部署

```bash
cp .env.example .env   # 按需修改配置
docker compose up -d

# 查看日志
docker compose logs -f data-service

# 停止
docker compose down
```

### 连接外部 MongoDB / Redis

```bash
# 在 .env 中指定外部服务地址
MONGODB_HOST=192.168.1.100
REDIS_HOST=192.168.1.101
DOCKER_CONTAINER=false
```

### 加入现有 Docker 网络（服务发现）

```yaml
# 在你的 docker-compose.yml 中引用已有的 mongodb / redis 服务
services:
  data-service:
    image: trading-data-service:latest
    environment:
      DOCKER_CONTAINER: "true"   # 自动使用 mongodb / redis 服务名
    networks:
      - your-existing-network
```

## API 接口

### 认证

```bash
# 登录（默认账号 admin / admin123）
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### 股票数据

```bash
TOKEN="<access_token>"

# A 股列表
curl http://localhost:8001/api/stocks/list \
  -H "Authorization: Bearer $TOKEN"

# 历史 K 线
curl "http://localhost:8001/api/stocks/000001/history?start_date=2024-01-01&end_date=2024-03-31" \
  -H "Authorization: Bearer $TOKEN"

# 搜索股票
curl -G "http://localhost:8001/api/stocks/search" \
  --data-urlencode "keyword=平安" \
  -H "Authorization: Bearer $TOKEN"
```

### 技术指标

```bash
# 全部指标
curl "http://localhost:8001/api/technical/000001" \
  -H "Authorization: Bearer $TOKEN"

# 指定指标（ma,macd,rsi,boll,kdj,atr）
curl "http://localhost:8001/api/technical/000001?indicators=ma,macd,rsi" \
  -H "Authorization: Bearer $TOKEN"
```

### 多市场

```bash
curl http://localhost:8001/api/markets -H "Authorization: Bearer $TOKEN"
curl http://localhost:8001/api/markets/CN/providers -H "Authorization: Bearer $TOKEN"
```

## 关键环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `MONGODB_HOST` | `localhost` | MongoDB 地址（Docker 内自动为 `mongodb`） |
| `REDIS_HOST` | `localhost` | Redis 地址（Docker 内自动为 `redis`） |
| `JWT_SECRET` | `change-me-in-production` | **生产环境必须修改** |
| `DEFAULT_CHINA_DATA_SOURCE` | `akshare` | A 股数据源 |
| `TUSHARE_TOKEN` | — | Tushare Pro Token（可选） |
| `DOCKER_CONTAINER` | `false` | `true` 时启用容器服务发现 |

完整变量列表见 [`.env.example`](.env.example)。

## 测试

```bash
pip install -e ".[dev]"
python -m pytest tests/ -v
```

## 项目结构

```
.
├── data_service/         ← Python 包
│   ├── layers/           ←   数据流各层实现
│   ├── routers/          ←   FastAPI 路由
│   ├── services/         ←   业务逻辑服务
│   ├── db/               ←   数据库连接管理
│   ├── models/           ←   Pydantic 数据模型
│   ├── config.py         ←   统一配置（含服务发现）
│   └── main.py           ←   FastAPI 应用入口
├── tests/                ← 测试
├── pyproject.toml
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── VERSION
```

## 相关项目

- [TradingAgents-CN](https://github.com/hsliuping/TradingAgents-CN): 智能量化交易多 Agent 框架

