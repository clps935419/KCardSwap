.PHONY: help dev up down logs test lint clean build

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

dev: ## Start development environment
	docker compose up -d

up: dev ## Alias for dev

down: ## Stop all services
	docker compose down

logs: ## View logs from all services
	docker compose logs -f

logs-backend: ## View backend logs only
	docker compose logs -f backend

logs-kong: ## View Kong logs only
	docker compose logs -f kong

logs-db: ## View database logs only
	docker compose logs -f db

test: ## Run backend tests
	cd apps/backend && pytest -v

lint: ## Run linter on backend code
	cd apps/backend && flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

clean: ## Stop services and remove volumes
	docker compose down -v

build: ## Rebuild all containers
	docker compose build

restart: ## Restart all services
	docker compose restart

ps: ## Show running containers
	docker compose ps

shell-backend: ## Open shell in backend container
	docker compose exec backend bash

shell-db: ## Open psql in database container
	docker compose exec db psql -U kcardswap -d kcardswap

init-db: ## Initialize database schema
	docker compose exec db psql -U kcardswap -d kcardswap -f /docker-entrypoint-initdb.d/init.sql

health: ## Check health of all services
	@echo "Checking health endpoints..."
	@curl -s http://localhost:8000/health || echo "Backend: DOWN"
	@echo ""
	@curl -s http://localhost:8080/api/v1/health || echo "Kong Proxy: DOWN"
	@echo ""
	@docker compose ps

seed: ## Seed database with test data (Phase 10)
	@echo "Seed functionality not yet implemented (Phase 10)"

init-admin: ## Initialize default admin user (idempotent)
	cd apps/backend && python scripts/init_admin.py

init-admin-docker: ## Initialize default admin in Docker container
	docker compose exec backend python scripts/init_admin.py

create-admin: ## Create a new admin user (interactive)
	cd apps/backend && python scripts/create_admin.py

setup: ## Initial setup - copy env and start services
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env file - please update with your values"; fi
	@make dev
	@echo "Waiting for services to start..."
	@sleep 10
	@make health
