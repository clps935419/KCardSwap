# KCardSwap Backend (FastAPI)

## 環境變數
- `DATABASE_URL`: 例如 `postgresql://kcardswap:kcardswap@db:5432/kcardswap`
- `GCS_BUCKET`: 例如 `kcardswap-dev`
- `JWT_SECRET`: 用於簽發 JWT 的密鑰（開發可暫用）

## 開發啟動
```bash
# 以 docker-compose 啟動整套環境
docker compose up -d

# 本機啟動（不使用 compose）
pip install fastapi uvicorn psycopg2-binary
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 結構建議
```
apps/backend/
  app/
    main.py
    routers/
      auth.py
      profile.py
      cards.py
      nearby.py
      social.py
      chat.py
      trade.py
      biz.py
    services/
    models/
    db/
```

## 測試
```bash
pip install pytest pytest-asyncio httpx
pytest -q
```

## 注意事項
- 與 Kong 連接路徑統一為 `/api/v1/*`
- 錯誤回應格式 `{ data: null, error: { code, message } }`
- 超限錯誤碼：`422_LIMIT_EXCEEDED`；未授權：`401_UNAUTHORIZED`
