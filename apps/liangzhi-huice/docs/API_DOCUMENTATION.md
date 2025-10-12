# 量化交易系统API文档

## 概述

本文档描述了量化交易系统的RESTful API接口。系统基于FastAPI + TimescaleDB构建，提供高性能的时序数据处理和实时交易功能。

## 主要功能

- **用户认证**: JWT令牌认证，支持注册、登录、权限管理
- **K线数据**: 多时间周期的OHLCV数据查询和实时推送
- **回测引擎**: 多策略回测，支持自定义策略和风险管理
- **实时通信**: WebSocket实时数据推送和交易信号
- **性能优化**: Redis缓存、连接池、限流保护

## 技术栈

- **后端框架**: FastAPI 0.104+
- **数据库**: PostgreSQL 15 + TimescaleDB 2.11
- **缓存**: Redis 7.0
- **消息队列**: Redis Pub/Sub
- **认证**: JWT (PyJWT)
- **数据处理**: Pandas, NumPy
- **技术指标**: TA-Lib

## 快速开始

### 1. 环境要求

- Python 3.11+
- PostgreSQL 15+ with TimescaleDB
- Redis 7.0+

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动服务

```bash
# 启动数据库和Redis
docker-compose up -d

# 启动API服务
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API认证

系统使用JWT Bearer Token认证。获取token后，在请求头中添加：

```
Authorization: Bearer <your_token>
```

## API端点

### 认证相关

#### 用户注册

```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123"
}
```

#### 用户登录

```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=testuser&password=password123
```

### K线数据

#### 获取K线数据

```http
GET /api/kline/data?symbol=BTCUSDT&timeframe=1h&start_time=2024-01-01T00:00:00Z&end_time=2024-01-02T00:00:00Z
Authorization: Bearer <token>
```

### 回测相关

#### 创建回测任务

```http
POST /api/backtest/create
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "MA策略回测",
  "symbol": "BTCUSDT",
  "timeframe": "1h",
  "start_time": "2024-01-01T00:00:00Z",
  "end_time": "2024-01-31T23:59:59Z",
  "strategy": "moving_average",
  "parameters": {
    "short_window": 10,
    "long_window": 30
  },
  "initial_capital": 10000
}
```

## 使用示例

### cURL示例

```bash
# 用户注册
curl -X POST http://localhost:8000/api/auth/register   -H "Content-Type: application/json"   -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'

# 用户登录
curl -X POST http://localhost:8000/api/auth/login   -H "Content-Type: application/x-www-form-urlencoded"   -d "username=testuser&password=password123"

# 获取K线数据
curl -X GET "http://localhost:8000/api/kline/data?symbol=BTCUSDT&timeframe=1h"   -H "Authorization: Bearer YOUR_TOKEN"
```

### Python示例

```python
import requests
import json

class TradingAPI:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.token = None
    
    def login(self, username, password):
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            data={"username": username, "password": password}
        )
        result = response.json()
        self.token = result["access_token"]
        return result
    
    def get_kline_data(self, symbol, timeframe, start_time=None, end_time=None):
        headers = {"Authorization": f"Bearer {self.token}"}
        params = {"symbol": symbol, "timeframe": timeframe}
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        
        response = requests.get(
            f"{self.base_url}/api/kline/data",
            headers=headers,
            params=params
        )
        return response.json()

# 使用示例
api = TradingAPI()
api.login("testuser", "password123")
kline_data = api.get_kline_data("BTCUSDT", "1h")
print(json.dumps(kline_data, indent=2))
```

### JavaScript示例

```javascript
class TradingAPI {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
        this.token = null;
    }
    
    async login(username, password) {
        const response = await fetch(`${this.baseURL}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `username=${username}&password=${password}`
        });
        const result = await response.json();
        this.token = result.access_token;
        return result;
    }
    
    async getKlineData(symbol, timeframe, startTime, endTime) {
        const params = new URLSearchParams({
            symbol,
            timeframe,
            ...(startTime && { start_time: startTime }),
            ...(endTime && { end_time: endTime })
        });
        
        const response = await fetch(`${this.baseURL}/api/kline/data?${params}`, {
            headers: {
                'Authorization': `Bearer ${this.token}`
            }
        });
        return await response.json();
    }
}

// 使用示例
const api = new TradingAPI();
api.login('testuser', 'password123').then(() => {
    return api.getKlineData('BTCUSDT', '1h');
}).then(data => {
    console.log('K线数据:', data);
});
```

## 错误处理

API使用标准HTTP状态码，错误响应格式如下：

```json
{
  "detail": "错误描述",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

常见错误码：
- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 未提供认证信息或认证失败
- `403 Forbidden`: 权限不足
- `404 Not Found`: 资源不存在
- `422 Unprocessable Entity`: 请求数据验证失败
- `429 Too Many Requests`: 请求频率超限
- `500 Internal Server Error`: 服务器内部错误

## 限流说明

为保护系统性能，API实施限流机制：
- 默认限制：100次请求/分钟
- 限流信息通过响应头返回：
  - `X-RateLimit-Limit`: 限制次数
  - `X-RateLimit-Remaining`: 剩余次数
  - `X-RateLimit-Reset`: 重置时间

## 数据格式说明

### 时间格式
所有时间字段使用ISO 8601格式：`YYYY-MM-DDTHH:MM:SSZ`

### 数值精度
- 价格：保留8位小数
- 数量：保留8位小数
- 百分比：保留4位小数

### 交易对格式
交易对使用大写字母，如：`BTCUSDT`、`ETHUSDT`

### 时间周期
支持的时间周期：
- `1m`, `3m`, `5m`, `15m`, `30m` - 分钟级
- `1h`, `2h`, `4h`, `6h`, `8h`, `12h` - 小时级
- `1d`, `3d`, `1w` - 日级和周级
- `1M` - 月级

## 联系方式

如有问题或建议，请联系：
- 邮箱: support@example.com
- 文档: http://localhost:8000/docs
- GitHub: https://github.com/example/trading-system
