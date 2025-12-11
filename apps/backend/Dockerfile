# Multi-stage Dockerfile for KCardSwap Backend
# Stage 1: Builder - 用於構建階段 (預留給未來需要編譯的依賴)
FROM python:3.11-slim AS builder

WORKDIR /app

# 複製 requirements.txt (由 Poetry 生成)
COPY requirements.txt .

# Stage 2: Runtime - 執行階段輕量映像
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 從 builder 複製 requirements.txt
COPY --from=builder /app/requirements.txt .

# 安裝生產依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式碼
COPY ./app ./app

# 暴露服務端口
EXPOSE 8000

# 啟動命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
