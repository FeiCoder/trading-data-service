---
name: stock-service-auth
description: 负责与 trading-data-service 进行身份认证，获取和刷新访问令牌 (JWT)。
---

# 身份认证管理 (Auth Management)

本 Skill 用于管理访问 API 所需的身份凭证。所有业务接口均受到 JWT (JSON Web Token) 的保护。

## 核心功能

1.  **用户登录**：提交用户名和密码，换取访问令牌。
2.  **令牌管理**：在后续请求中正确配置 Header。

## 接口规范

### 用户登录
- **路径**: `POST /api/auth/login`
- **请求体 (JSON)**:
    ```json
    {
      "username": "admin",
      "password": "admin123"
    }
    ```
- **响应**:
    ```json
    {
      "success": true,
      "data": {
        "access_token": "...",
        "token_type": "bearer"
      }
    }
    ```

## 默认配置

- **默认账号**: `admin`
- **默认密码**: `admin123`
- **令牌过期时间**: 默认 60 分钟。

## 使用流程建议

1.  在对话初始阶段或令牌过期时，由智能体首先调用登录接口。
2.  将获取到的 `access_token` 存储在环境变量或上下文变量中。
3.  在调用 `stock-query` 或 `technical-analysis` 时，在 Header 中加入 `Authorization: Bearer <TOKEN>`。

## 示例

```bash
# 获取 Token 并提取到变量
TOKEN=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | jq -r '.data.access_token')
```
