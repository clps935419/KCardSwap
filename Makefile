
.PHONY: help dev dev-build up down logs logs-backend logs-kong logs-db \
	test-unit-docker test-integration-docker test-docker ruff-docker clean build restart ps \
	shell-backend shell-db init-db health seed init-admin-docker setup generate-openapi-docker \
	prod-up prod-down

help: ## 顯示可用指令
	@echo '用法: make [target]'
	@echo ''
	@echo '可用指令:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-22s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

dev: ## 啟動開發環境（背景執行）
	@if [ ! -f .env ]; then \
		echo "錯誤: 找不到 .env 檔案"; \
		echo "請先執行 'make setup' 或手動從 .env.example 複製"; \
		exit 1; \
	fi
	docker compose up -d

dev-build: ## 重新建置並啟動開發環境
	@if [ ! -f .env ]; then \
		echo "錯誤: 找不到 .env 檔案"; \
		echo "請先執行 'make setup' 或手動從 .env.example 複製"; \
		exit 1; \
	fi
	docker compose up -d --build

up: dev ## dev 的別名

down: ## 停止所有服務
	docker compose down

prod-up: ## 啟動正式環境（使用 docker-compose.prod.yml）
	docker compose --env-file .env.prod -f docker-compose.yml -f docker-compose.prod.yml up -d --build

prod-down: ## 停止正式環境
	docker compose --env-file .env.prod -f docker-compose.yml -f docker-compose.prod.yml down

logs: ## 查看所有服務日誌
	docker compose logs -f

logs-backend: ## 查看後端日誌
	docker compose logs -f backend

logs-kong: ## 查看 Kong 日誌
	docker compose logs -f kong

logs-db: ## 查看資料庫日誌
	docker compose logs -f db

test-unit-docker: ## 在 Docker 中執行單元測試
	docker compose exec backend python -m pytest -v tests/unit

test-integration-docker: ## 在 Docker 中執行整合測試
	docker compose exec backend python -m pytest -v tests/integration

test-docker: ## 在 Docker 中執行全部測試
	docker compose exec backend python -m pytest -v

ruff-docker: ## 在 Docker 中執行 Ruff 檢查（含自動修正）
	docker compose exec backend python -m ruff check . --fix

clean: ## 停止服務並移除 volumes
	docker compose down -v

build: ## 重新建置所有容器
	docker compose build

restart: ## 重啟所有服務
	docker compose restart

ps: ## 顯示容器狀態
	docker compose ps

shell-backend: ## 進入後端容器 shell
	docker compose exec backend bash

shell-db: ## 進入資料庫 psql
	docker compose exec db psql -U kcardswap -d kcardswap

init-db: ## 初始化資料庫 schema
	docker compose exec db psql -U kcardswap -d kcardswap -f /docker-entrypoint-initdb.d/init.sql

health: ## 檢查服務健康狀態
	@echo "檢查健康端點..."
	@curl -s http://localhost:8000/health || echo "Backend: DOWN"
	@echo ""
	@docker compose ps

seed: ## 填入測試資料（尚未實作）
	@echo "Seed 功能尚未實作"

init-admin-docker: ## 在 Docker 中初始化預設管理員
	docker compose exec backend python scripts/init_admin.py

setup: ## 初始設定：複製 env 並啟動服務
	@if [ ! -f .env ]; then cp .env.example .env; echo "已建立 .env，請更新內容"; fi
	@make dev
	@echo "等待服務啟動..."
	@sleep 10
	@make health

generate-openapi-docker: ## 在 Docker 中產生 OpenAPI 規格
	docker compose exec backend python scripts/generate_openapi.py
