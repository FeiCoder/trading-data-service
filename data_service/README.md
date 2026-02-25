# TradingAgents-CN 数据管理服务

独立的股票数据管理微服务，参考 [TradingAgents-CN](https://github.com/hsliuping/TradingAgents-CN) 项目，专注于数据获取、缓存、处理和技术分析，提供标准化的 HTTP 接口。

## 功能特性

| 功能 | 说明 |
|------|------|
| 🔐 用户认证 | 基于 JWT 的无状态认证，用户信息存储于 MongoDB |
| 📊 股票数据管理 | A股 / 港股 / 美股历史 K 线及基础信息 |
| 🌐 多市场数据提供商 | AKShare（默认）/ Tushare Pro / BaoStock / yfinance / FinnHub |
| 🗄️ 多级缓存 | Redis → MongoDB → 文件，自动降级 |
| 📈 技术指标分析 | MA / EMA / MACD / RSI / 布林带 / KDJ / ATR |
| 🐳 Docker 独立部署 | 支持容器网络服务发现及外部数据库连接 |

## 分层架构

```
┌─────────────────────────────────────────────────────────────┐
│                    HTTP API Layer (FastAPI)                   │
│  /api/auth  /api/stocks  /api/markets  /api/technical        │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                     Analysis Layer                           │
│         MA / MACD / RSI / BOLL / KDJ / ATR                  │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                    Processing Layer                          │
│         数据清洗 / 格式化 / 标准化 / 衍生指标               │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      Cache Layer                             │
│         Redis (L1)  →  MongoDB (L2)  →  文件 (L3)           │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                   Acquisition Layer                          │
│    AKShare / Tushare / BaoStock / yfinance / FinnHub        │
└─────────────────────────────────────────────────────────────┘
```

## 快速开始

### 本地开发

```bash
# 复制环境配置
cp .env.data_service .env

# 编辑 .env，配置数据库连接
vim .env

# 启动服务
python -m uvicorn data_service.main:app --host 0.0.0.0 --port 8001 --reload

# 访问 API 文档
open http://localhost:8001/docs
```

### Docker 部署（包含 MongoDB + Redis）

```bash
# 使用独立 Docker Compose 配置
docker compose -f docker-compose.data_service.yml up -d

# 查看日志
docker compose -f docker-compose.data_service.yml logs -f data-service

# 停止服务
docker compose -f docker-compose.data_service.yml down
```

### 与现有服务协同部署（服务发现）

当数据管理服务与其他服务在同一 Docker 网络中运行时，只需加入该网络，服务会**自动**使用容器服务名（`mongodb` / `redis`）进行连接，无需额外配置。

```yaml
# 在主 docker-compose.yml 中加入现有网络
services:
  data-service:
    image: tradingagents-data-service:latest
    networks:
      - tradingagents-network   # 加入现有网络即可自动发现 mongodb/redis
    environment:
      DOCKER_CONTAINER: "true"
```

### 连接外部数据库

```bash
# 在 .env 中配置外部数据库地址
MONGODB_HOST=192.168.1.100
MONGODB_PORT=27017
REDIS_HOST=192.168.1.101
REDIS_PORT=6379
```

## API 接口

服务启动后可通过 `/docs` 查看完整的 OpenAPI 文档。

### 认证

```bash
# 登录获取 Token（默认账号 admin/admin123）
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### 股票数据

```bash
TOKEN="<your-jwt-token>"

# 获取 A 股列表
curl http://localhost:8001/api/stocks/list \
  -H "Authorization: Bearer $TOKEN"

# 获取历史 K 线
curl "http://localhost:8001/api/stocks/000001/history?start_date=2024-01-01&end_date=2024-03-31" \
  -H "Authorization: Bearer $TOKEN"

# 搜索股票
curl -G "http://localhost:8001/api/stocks/search" \
  --data-urlencode "keyword=平安" \
  -H "Authorization: Bearer $TOKEN"
```

### 技术分析

```bash
# 获取技术指标（MA / MACD / RSI / 全部）
curl "http://localhost:8001/api/technical/000001?indicators=ma,macd,rsi" \
  -H "Authorization: Bearer $TOKEN"
```

### 多市场查询

```bash
# 查看支持的市场列表
curl http://localhost:8001/api/markets \
  -H "Authorization: Bearer $TOKEN"

# 查看 A 股数据提供商
curl http://localhost:8001/api/markets/CN/providers \
  -H "Authorization: Bearer $TOKEN"
```

## 环境变量

详见 [`.env.data_service`](../.env.data_service) 中的注释说明。关键配置：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `MONGODB_HOST` | `localhost` / `mongodb`(Docker) | MongoDB 地址 |
| `REDIS_HOST` | `localhost` / `redis`(Docker) | Redis 地址 |
| `JWT_SECRET` | `change-me-in-production` | **生产环境必须修改** |
| `DEFAULT_CHINA_DATA_SOURCE` | `akshare` | A股数据源 |
| `TUSHARE_TOKEN` | — | Tushare Pro Token（可选） |
| `DOCKER_CONTAINER` | `false` | 设为 `true` 启用服务发现 |

## 测试

```bash
python -m pytest tests/test_data_service.py -v
```

---

## 将 data_service 抽离为独立 git 仓库

`data_service/standalone/` 目录包含了将本模块提取为独立项目所需的全部文件，一条命令即可完成：

```bash
# 在 TradingAgents-CN 项目根目录下执行
chmod +x data_service/standalone/extract.sh
./data_service/standalone/extract.sh ~/projects/trading-data-service
```

脚本会在目标路径生成以下结构（完整的独立 git 仓库）：

```
trading-data-service/
├── data_service/        ← Python 包（原 data_service/ 内容）
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── db/
│   ├── layers/
│   ├── models/
│   ├── routers/
│   └── services/
├── tests/               ← 独立测试套件
│   └── test_data_service.py
├── pyproject.toml       ← Python 包定义
├── requirements.txt     ← 直接 pip 安装依赖
├── Dockerfile           ← 独立镜像（无 tradingagents 依赖）
├── docker-compose.yml   ← 独立部署
├── .gitignore
├── .env.example
├── VERSION
└── README.md
```

完成后按提示推送到新的远程仓库：

```bash
cd ~/projects/trading-data-service
git remote add origin https://github.com/<你的用户名>/trading-data-service.git
git push -u origin main
```

> **手动提取**（如果不想运行脚本）：
>
> ```bash
> mkdir trading-data-service && cd trading-data-service
> git init -b main
> cp -r /path/to/TradingAgents-CN/data_service .
> cp data_service/standalone/{pyproject.toml,requirements.txt,Dockerfile,docker-compose.yml,VERSION,README.md} .
> cp data_service/standalone/.gitignore data_service/standalone/.env.example .
> cp -r data_service/tests tests
> rm -rf data_service/standalone
> git add . && git commit -m "feat: initial commit"
> ```
