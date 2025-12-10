# Kong Gateway 設定

## 目錄
- `kong.yaml`: 宣告式設定（服務、路由與插件）

## 啟動
```bash
docker compose up -d kong
```

## 主要路由
- 服務：`backend` → `http://backend:8000`
- 路由：`/api/v1/*` 透過 Kong 代理到後端

## 插件
- `cors`: 允許跨域與授權標頭
- `request-size-limiting`: 限制請求大小（預設 6MB）
- `rate-limiting`: 本地速率限制（預設每分鐘 120 次）

## 管理介面
- Admin API：`http://localhost:8001`
- Proxy：`http://localhost:8080`

## 驗證建議
- 之後可加入 `jwt` 插件，對接後端簽發的 JWT
- 針對不同會員等級，可用 `rate-limiting-advanced` 或自訂策略
