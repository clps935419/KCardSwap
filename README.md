# KCardSwap - Card Exchange Platform

A card trading platform built with FastAPI, Kong API Gateway, and PostgreSQL.

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
- Kong Gateway: http://localhost:8080
- Kong Admin: http://localhost:8001
- PostgreSQL: localhost:5432

For deterministic client generation (cloud agent / CI), keep an OpenAPI snapshot in the repository:

- `openapi/README.md`

## 📁 Project Structure

```
KCardSwap/
├── apps/
│   └── backend/          # FastAPI backend application
│       ├── app/
│       │   ├── main.py   # Application entry point
│       │   ├── config.py # Settings / env config
│       │   ├── injector.py # IoC container setup
│       │   ├── modules/  # Feature modules (e.g. identity, social, posts)
│       │   └── shared/   # Shared infrastructure / cross-cutting concerns
│       ├── alembic/      # Database migrations
│       ├── tests/        # Test files
│       ├── pyproject.toml # Poetry dependencies
│       ├── poetry.lock   # Locked dependencies
│       └── Dockerfile    # Multi-stage build
│   └── mobile/           # Expo (React Native) mobile app
├── gateway/
│   └── kong/             # Kong API Gateway configuration
│       └── kong.yaml     # Declarative config
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
└── SECRETS.md           # Secrets management guide
```

## 🛠️ Development

Backend routes are registered in `apps/backend/app/main.py`; individual routers live under each module’s `presentation/routers/`.

### Available Commands

```bash
make help           # Show all available commands
make dev            # Start development environment
make down           # Stop all services
make logs           # View logs from all services
make test           # Run tests
make lint           # Run linter
make clean          # Stop services and remove volumes
make health         # Check service health
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

### Mobile Development

```bash
cd apps/mobile
npm install --legacy-peer-deps
npm start
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

All API endpoints are prefixed with `/api/v1/` and routed through Kong Gateway:

```
GET  /health              # Health check (direct)
GET  /api/v1/health       # Health check (via Kong)
GET  /api/v1/docs         # API documentation
```

### Example Request via Kong

```bash
# Direct to backend
curl http://localhost:8000/api/v1/health

# Via Kong Gateway (with rate limiting, CORS, etc.)
curl http://localhost:8080/api/v1/health
```

## 🔐 Security & Secrets

See [SECRETS.md](SECRETS.md) for detailed secrets management strategy.

**Important:**
- Never commit `.env` file
- Rotate secrets regularly
- Use different secrets for each environment

## 🚢 Deployment

### Phase 0 Status (Current)

- [x] Mono-repo structure
- [x] Docker Compose setup
- [x] Kong API Gateway configuration
- [x] Backend basic structure
- [x] Database initialization
- [x] CI/CD workflows
- [x] Secrets management documentation

### Next Phases

See [specs/001-kcardswap-complete-spec/tasks.md](specs/001-kcardswap-complete-spec/tasks.md) for complete roadmap.

## 📊 Tech Stack

- **Backend**: Python 3.11, FastAPI, Uvicorn
- **Database**: PostgreSQL 15
- **API Gateway**: Kong 3.7
- **Container**: Docker & Docker Compose
- **CI/CD**: GitHub Actions
- **Testing**: pytest, httpx

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linter
4. Submit a pull request

CI will automatically run:
- Python linting (ruff)
- Unit tests (pytest)
- Build verification
- PR validation checks

## 📚 Documentation

- [Specification](specs/001-kcardswap-complete-spec/spec.md) - Complete feature specification
- [Technical Plan](specs/001-kcardswap-complete-spec/plan.md) - Architecture and technical design
- [Tasks](specs/001-kcardswap-complete-spec/tasks.md) - Implementation roadmap
- [Secrets Management](SECRETS.md) - Security and secrets guide
- [Backend README](apps/backend/README.md) - Backend-specific documentation
- [Mobile README](apps/mobile/README.md) - Mobile app documentation
- [OpenAPI Snapshot Guide](openapi/README.md) - How to generate/update OpenAPI snapshot
- [PR Merge Reports Index](reports/README.md) - Consolidated completion reports and verification notes

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

### Kong routing issues

```bash
# Verify Kong configuration
docker compose exec kong kong config parse /kong/declarative/kong.yaml

# Check Kong logs
make logs-kong
```

## 📄 License

[Add license information]

## 👥 Team

[Add team/contact information]
