# KCardSwap - Card Exchange Platform

A social platform for discussing idol photocards, built with FastAPI, PostgreSQL, and Next.js.

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Make (optional, for convenience commands)

### Setup

**Quick Setup (Recommended):**
```bash
make setup
```

This will automatically create the `.env` file and start all services.

**Manual Setup:**

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd KCardSwap
   ```

2. Copy environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

   **Note**: The backend uses Google Cloud Storage (GCS) for image uploads. Provide a service account key file and set the related env vars (for example `GCS_CREDENTIALS_PATH` and `GCS_BUCKET_NAME`).

3. Start all services:
   ```bash
   # Build and start all services (first time or after Dockerfile changes)
   docker compose up --build -d
   
   # Or for subsequent runs
   docker compose up -d
   
   # Or simply use
   make dev
   ```
   
   **Note**: The backend now uses Poetry for dependency management and includes:
   - Automatic database migrations via Alembic on startup
   - Hot-reload for development (via docker-compose.override.yml)
   - Multi-stage Docker build for optimized images

4. Verify services are running:
   ```bash
   make health
   ```

**Troubleshooting:** If you encounter any issues, see [DOCKER_TROUBLESHOOTING.md](./DOCKER_TROUBLESHOOTING.md)

Access points:
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/v1/docs
- OpenAPI JSON: http://localhost:8000/api/v1/openapi.json
- Web App (dev): http://localhost:3000
- PostgreSQL: localhost:5432

For deterministic client generation (cloud agent / CI), keep an OpenAPI snapshot in the repository:

- `openapi/README.md`

## 📁 Project Structure

```
KCardSwap/
├── apps/
│   ├── backend/          # FastAPI backend application
│   │   ├── app/
│   │   │   ├── main.py   # Application entry point
│   │   │   ├── config.py # Settings / env config
│   │   │   ├── injector.py # IoC container setup
│   │   │   ├── modules/  # Feature modules (e.g. identity, social, posts)
│   │   │   └── shared/   # Shared infrastructure / cross-cutting concerns
│   │   ├── alembic/      # Database migrations
│   │   ├── tests/        # Test files
│   │   ├── pyproject.toml # Poetry dependencies
│   │   ├── poetry.lock   # Locked dependencies
│   │   └── Dockerfile    # Multi-stage build
│   └── web/              # Next.js web app (App Router)
├── infra/
│   └── db/               # Database scripts
│       └── init.sql      # Database-level setup only
├── openapi/               # OpenAPI snapshot (used for SDK generation)
├── specs/                # Feature specifications
├── .github/
│   └── workflows/        # CI/CD workflows
├── docker-compose.yml    # Container orchestration
├── docker-compose.override.yml  # Development overrides
├── Makefile             # Development commands
```

## 🛠️ Development

Backend routes are registered in `apps/backend/app/main.py`; individual routers live under each module’s `presentation/routers/`.

### Available Commands

```bash
make help                 # Show all available commands
make dev                  # Start development environment
make dev-build            # Rebuild and start development environment
make down                 # Stop all services
make logs                 # View logs from all services
make logs-backend         # View backend logs
make logs-db              # View database logs
make test-docker          # Run all tests in Docker
make ruff-docker          # Run Ruff checks in Docker (with fix)
make clean                # Stop services and remove volumes
make reset-db             # Clear all volumes (including DB data)
make build                # Rebuild all containers
make restart              # Restart all services
make ps                   # Show container status
make shell-backend        # Enter backend container shell
make shell-db             # Enter database psql
make init-db              # Initialize database schema
make init-admin-docker    # Initialize default admin in Docker
make health               # Check service health
make setup                # Initial setup (copy env and start)
make generate-openapi-docker # Generate OpenAPI spec in Docker
make prod-up              # Start production environment
make prod-down            # Stop production environment
make prod-web-build       # Build production web image
```

### Backend Development

```bash
# View backend logs
make logs-backend

# Run tests
cd apps/backend
poetry run pytest -v

# Run linter
cd apps/backend
poetry run ruff check .

# Access backend shell
make shell-backend
```

### Web Development

```bash
cd apps/web
npm install --legacy-peer-deps
npm run dev
```

### Database

```bash
# Access PostgreSQL
make shell-db

# Re-initialize database
make init-db
```

## 🧪 Testing

Run all tests:
```bash
cd apps/backend
poetry run pytest -v --cov=app
```

Run specific test file:
```bash
cd apps/backend
pytest tests/test_main.py -v
```

## 📝 API Documentation

Once the services are running, access the interactive API documentation:

- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

### API Routes

All API endpoints are prefixed with `/api/v1/`:

```
GET  /health              # Health check (direct)
GET  /api/v1/health       # Health check
GET  /api/v1/docs         # API documentation
```

### Example Request

```bash
curl http://localhost:8000/api/v1/health
```

## 📊 Tech Stack

- **Backend**: Python 3.11, FastAPI, Uvicorn
- **Database**: PostgreSQL 15
- **Web**: Next.js (App Router)
- **Container**: Docker & Docker Compose
- **CI/CD**: GitHub Actions
- **Testing**: pytest, httpx

## 🐛 Troubleshooting

### Services won't start

```bash
# Check service status
docker compose ps

# View logs
docker compose logs

# Restart services
docker compose restart
```

### Database connection issues

```bash
# Verify database is running
docker compose ps db

# Check database logs
make logs-db

# Test connection
docker compose exec db pg_isready -U kcardswap
```


## 📄 License

[Add license information]

## 👥 Team

[Add team/contact information]
