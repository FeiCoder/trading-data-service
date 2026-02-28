# Trading Data Service - HTTP API 接口文档

本文档详细说明了 `trading-data-service` 提供的 RESTful API 接口。

## 基础信息
- **Base URL**: `http://localhost:8001`
- **认证方式**: 
    - **JWT**: 在 Header 中加入 `Authorization: Bearer <TOKEN>`
    - **API Key**: 在 Header 中加入 `X-API-Key: <YOUR_KEY>` (需在服务端配置 `AUTH_API_KEY`)

---

## 🔐 认证 (Auth)

### 1. 用户登录
获取 JWT 访问令牌。
- **URL**: `/api/auth/login`
- **Method**: `POST`
- **Payload**:
  ```json
  {
    "username": "admin",
    "password": "admin123"
  }
  ```
- **Response**: `{"success": true, "data": {"access_token": "...", "token_type": "bearer"}}`

### 2. 获取当前用户信息
- **URL**: `/api/auth/me`
- **Method**: `GET`
- **Auth Required**: Yes

---

## 📊 股票查询 (Stocks)

### 1. 获取股票列表
按市场获取完整的股票清单。
- **URL**: `/api/stocks/list`
- **Method**: `GET`
- **Params**:
    - `market` (string): 市场代码 (CN, HK, US)。
    - `force_refresh` (bool): 是否跳过缓存强制拉取。

### 2. 搜索股票
根据代码或名称模糊匹配。
- **URL**: `/api/stocks/search`
- **Method**: `GET`
- **Params**:
    - `keyword` (string, 必填): 关键词。
    - `market` (string): 市场代码。

### 3. 获取历史 K 线
获取标准化的 OHLCV 数据。
- **URL**: `/api/stocks/{symbol}/history`
- **Method**: `GET`
- **Params**:
    - `start_date` (string): YYYY-MM-DD。
    - `end_date` (string): YYYY-MM-DD。
    - `market` (string): 市场代码。

---

## 📈 技术分析 (Technical)

### 1. 获取技术指标
计算 MA, MACD, RSI, BOLL, KDJ, ATR 等指标。
- **URL**: `/api/technical/{symbol}`
- **Method**: `GET`
- **Params**:
    - `indicators` (string): 逗号分隔的指标名（如 `ma,macd`）。
    - `start_date` / `end_date`: 日期范围。
- **Response**: 返回 `latest` (最新值) 和 `history` (历史序列)。

---

## 🌐 市场信息 (Markets)

### 1. 获取支持的市场
- **URL**: `/api/markets`
- **Method**: `GET`

### 2. 查看数据源状态
- **URL**: `/api/markets/{market}/providers`
- **Method**: `GET`

---

## 📰 财经新闻 (News)

### 1. 获取财经新闻原始数据
- **URL**: `/api/news`
- **Method**: `GET`
- **Params**:
    - `source` (string): 新闻源，支持 `all` / `sina` / `cls_hot` / `wallstreetcn` / `yahoo_rss`。
    - `limit` (int): 返回条数，范围 1-100。
    - `start_datetime` (string, optional): 开始时间（ISO 8601），用于历史新闻按时间过滤。
    - `end_datetime` (string, optional): 结束时间（ISO 8601），用于历史新闻按时间过滤。
