# Multi-stage Dockerfile for KCardSwap Backend with Poetry
# Stage 1: Builder - 安裝依賴
FROM python:3.11-slim AS builder

# 安裝 Poetry
RUN pip install --no-cache-dir poetry==1.7.1

WORKDIR /app

# 設定 Poetry 不建立虛擬環境（因為已在容器中）
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# 複製依賴定義檔案
COPY pyproject.toml poetry.lock ./

# 僅安裝生產依賴（包含 alembic）
RUN poetry install --only main --no-root && rm -rf $POETRY_CACHE_DIR

# Stage 2: Runtime - 執行階段輕量映像
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 從 builder 複製已安裝的 Python 套件
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 複製應用程式碼和 Alembic 配置
COPY ./app ./app
COPY ./alembic ./alembic
COPY ./alembic.ini ./alembic.ini

# 暴露服務端口
EXPOSE 8000

# 建立啟動腳本以先執行 migrations 再啟動應用
RUN echo '#!/bin/bash\n\
set -e\n\
echo "Running database migrations..."\n\
alembic upgrade head\n\
echo "Starting application..."\n\
exec uvicorn app.main:app --host 0.0.0.0 --port 8000' > /app/start.sh \
    && chmod +x /app/start.sh

# 啟動命令：先執行 migrations，然後啟動應用
CMD ["/app/start.sh"]
