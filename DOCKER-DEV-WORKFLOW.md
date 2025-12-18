# Docker Development Workflow - Scripts Directory

## 問題

當在 Dockerfile 中使用 `COPY ./scripts ./scripts` 時，每次修改 scripts 目錄中的檔案（如新增 init data 腳本），都需要重新 build Docker image，影響開發效率。

## 業界最佳實務解決方案

### 開發模式（Development）vs 生產模式（Production）

業界標準做法是**分離開發和生產環境的配置**：

#### 🔧 開發模式：使用 Volume Mount
- **方式**：透過 `docker-compose.override.yml` 掛載本地目錄
- **優點**：
  - ✅ 檔案修改即時生效，無需重新 build
  - ✅ 快速開發迭代
  - ✅ 支援 hot reload
- **缺點**：
  - ⚠️ 需要本地檔案存在
  - ⚠️ 不適合生產環境

#### 🚀 生產模式：使用 Dockerfile COPY
- **方式**：在 Dockerfile 中 `COPY ./scripts ./scripts`
- **優點**：
  - ✅ Image 自包含，無需外部依賴
  - ✅ 部署可靠且一致
  - ✅ 安全性高
- **缺點**：
  - ⚠️ 修改需要重新 build

## 本專案的實作

### 1. Dockerfile（生產用）

```dockerfile
# apps/backend/Dockerfile
COPY ./app ./app
COPY ./alembic ./alembic
COPY ./alembic.ini ./alembic.ini
COPY ./scripts ./scripts  # 生產環境：打包進 image
```

### 2. docker-compose.override.yml（開發用）

```yaml
# docker-compose.override.yml
services:
  backend:
    volumes:
      - ./apps/backend/app:/app/app
      - ./apps/backend/alembic:/app/alembic
      - ./apps/backend/scripts:/app/scripts  # 開發環境：掛載本地目錄
```

### 3. 運作原理

Docker Compose 會自動：
1. 讀取 `docker-compose.yml`（基礎配置）
2. **自動合併** `docker-compose.override.yml`（開發配置）
3. Volume mount 會**覆蓋** Dockerfile 中 COPY 的內容

這意味著：
- **開發時**：`./apps/backend/scripts` 的修改會即時反映在容器中
- **生產時**：只使用 `docker-compose.yml`，scripts 已打包在 image 中

## 使用方式

### 開發模式（預設）

```bash
# 啟動開發環境（自動使用 override）
docker compose up -d

# 修改 scripts/init_admin.py
vim apps/backend/scripts/init_admin.py

# 容器會自動看到修改，無需重新 build！
docker compose restart backend
```

### 生產模式

```bash
# 明確指定不使用 override 檔案
docker compose -f docker-compose.yml up -d

# 或建立生產專用的 compose 檔案
docker compose -f docker-compose.prod.yml up -d
```

## 優勢總結

### ✅ 開發體驗優化
- 修改 `init_admin.py` 或新增 init data 腳本時，**不需要重新 build**
- 只需要 `docker compose restart backend` 即可
- 快速迭代，提升開發效率

### ✅ 生產環境安全
- Dockerfile 仍然包含 `COPY ./scripts`
- 生產 image 是自包含的
- 不依賴外部 volume mount

### ✅ 符合業界標準
- Docker 官方推薦做法
- 類似專案（Django, Rails, Node.js）都使用此模式
- 清楚分離開發和生產配置

## 其他已掛載的目錄

本專案已經在 `docker-compose.override.yml` 中掛載：
- ✅ `./apps/backend/app:/app/app` - 應用程式碼
- ✅ `./apps/backend/alembic:/app/alembic` - 資料庫遷移
- ✅ `./apps/backend/scripts:/app/scripts` - 初始化腳本 ⭐ **新增**
- ✅ `./apps/backend/pyproject.toml:/app/pyproject.toml:ro` - Poetry 配置
- ✅ `./apps/backend/poetry.lock:/app/poetry.lock:ro` - 依賴鎖定

## 參考資料

- [Docker Official Docs - Use volumes](https://docs.docker.com/storage/volumes/)
- [Docker Compose Override](https://docs.docker.com/compose/extends/)
- [Best practices for development workflows](https://docs.docker.com/develop/dev-best-practices/)

## 常見問題

### Q1: 為什麼不直接刪除 Dockerfile 中的 COPY？

A: 生產環境需要自包含的 image。如果刪除 COPY，生產部署時 scripts 目錄會不存在。

### Q2: Volume mount 會不會影響效能？

A: 在 Linux/Mac 上影響極小。在 Windows 上可能有些許效能影響，但對於腳本檔案（通常很小）影響可忽略。

### Q3: 如何確認是否使用了 override？

```bash
# 查看實際使用的配置
docker compose config

# 會看到 volumes 包含本地目錄掛載
```

### Q4: CI/CD 會不會用到 override？

A: 預設不會。CI/CD 通常只使用 `docker-compose.yml` 或生產專用的 compose 檔案。

## 結論

透過 `docker-compose.override.yml` 掛載 scripts 目錄，達到：
- 🚀 開發時無需重新 build（快速迭代）
- 🔒 生產時自包含 image（安全可靠）
- ✅ 符合業界最佳實務

這是 Docker 開發的標準模式，被廣泛應用於各種專案中。
