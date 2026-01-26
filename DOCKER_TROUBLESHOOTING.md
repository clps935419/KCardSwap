# Docker Troubleshooting Guide

本文檔記錄了常見的 Docker 建構和執行問題及其解決方案。

## 問題 1: Container kcardswap-backend exited (1)

### 症狀
```
✘ Container kcardswap-backend            Error depen...
dependency failed to start: container kcardswap-backend exited (1)
```

### 原因
缺少 `.env` 環境變數檔案。Docker Compose 在啟動容器時需要讀取 `.env` 檔案。

### 解決方案

**方法 1: 使用 setup 命令（推薦給首次設定）**
```bash
make setup
```

**方法 2: 手動複製環境變數檔案**
```bash
cp .env.example .env
# 編輯 .env 填入你的設定值（如果需要）
make dev
```

### 預防措施
- 現在 `make dev` 會自動檢查 `.env` 是否存在
- 如果檔案不存在，會顯示明確的錯誤訊息

---

## 問題 2: SSL Certificate Verification Failed

### 症狀
Docker 建構時出現 SSL 憑證驗證錯誤：
```
SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: 
self-signed certificate in certificate chain
```

### 原因
- 企業代理伺服器 (Corporate Proxy)
- SSL 攔截/檢查 (SSL Inspection)
- 自簽憑證 (Self-signed Certificate)
- CI/CD 環境的網路限制

### 解決方案

本專案的 Dockerfile 已經包含了 SSL 問題的解決方案：

1. **安裝 ca-certificates 套件**
2. **使用 `--trusted-host` 標記**
3. **配置 Poetry 使用傳統的 pip installer**

如果仍然遇到問題，可以嘗試：

**方法 1: 停用 BuildKit**
```bash
export DOCKER_BUILDKIT=0
make dev
```

**方法 2: 使用 HTTP 代理設定（如果你的環境有代理）**
```bash
# 在 .env 檔案中加入
HTTP_PROXY=http://your-proxy:port
HTTPS_PROXY=http://your-proxy:port
NO_PROXY=localhost,127.0.0.1
```

**方法 3: 配置 Docker daemon（需要管理員權限）**

編輯或建立 `/etc/docker/daemon.json`:
```json
{
  "insecure-registries": ["pypi.org", "files.pythonhosted.org"]
}
```

重啟 Docker:
```bash
sudo systemctl restart docker
```

---

## 問題 3: Port Already in Use

### 症狀
```
Error: bind: address already in use
```

### 解決方案

**檢查佔用的 port:**
```bash
# 檢查 8000 (backend)
lsof -i :8000
# 檢查 8080 (kong)
lsof -i :8080
# 檢查 5432 (postgres)
lsof -i :5432
```

**停止佔用的服務或改用其他 port:**
```bash
# 停止現有容器
make down

# 或強制移除
docker compose down -v

# 如果需要改 port，編輯 docker-compose.yml 中的 ports 設定
```

---

## 問題 4: Database Connection Failed

### 症狀
Backend 無法連接到資料庫

### 解決方案

**檢查資料庫是否健康:**
```bash
docker compose ps
```

**查看資料庫日誌:**
```bash
make logs-db
```

**重新初始化資料庫:**
```bash
make clean    # 停止並移除 volumes
make setup    # 重新建立環境
```

---

## 問題 5: Image Build is Too Slow

### 解決方案

**使用 BuildKit 快取:**
```bash
export DOCKER_BUILDKIT=1
docker compose build --no-cache backend
```

**清理舊的建構快取:**
```bash
docker builder prune -af
```

---

## 有用的除錯命令

### 查看容器日誌
```bash
make logs              # 所有服務
make logs-backend      # 只看 backend
make logs-db           # 只看資料庫
make logs-kong         # 只看 Kong
```

### 進入容器 shell
```bash
make shell-backend     # 進入 backend 容器
make shell-db          # 進入資料庫 psql
```

### 檢查服務健康狀態
```bash
make health           # 檢查所有服務
make ps              # 顯示運行中的容器
```

### 重建容器
```bash
make build           # 重建所有容器
make restart         # 重啟服務
```

### 完全清理並重建
```bash
make clean           # 停止並移除 volumes
make build           # 重建容器
make setup           # 啟動並檢查健康狀態
```

---

## 取得更多協助

如果以上解決方案都無法解決你的問題：

1. 檢查 GitHub Issues 是否有類似問題
2. 查看完整的容器日誌: `docker compose logs backend`
3. 提供以下資訊來報告問題：
   - 作業系統和版本
   - Docker 和 Docker Compose 版本
   - 完整的錯誤訊息
   - 相關的日誌輸出
