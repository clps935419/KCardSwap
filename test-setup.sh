#!/bin/bash
# Test script to verify KCardSwap setup

set -e

echo "🧪 Testing KCardSwap Setup..."
echo ""

# Start services
echo "📦 Starting services..."
docker compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 30

# Check if containers are running
echo ""
echo "🔍 Checking container status..."
docker compose ps

# Test backend health endpoint
echo ""
echo "🏥 Testing backend health endpoint..."
BACKEND_HEALTH=$(curl -s http://localhost:8000/health || echo "FAILED")
if echo "$BACKEND_HEALTH" | grep -q "healthy"; then
    echo "✓ Backend health check passed"
else
    echo "✗ Backend health check failed"
    echo "Response: $BACKEND_HEALTH"
fi

# Test API health endpoint via backend
echo ""
echo "🏥 Testing API health endpoint (direct)..."
API_HEALTH=$(curl -s http://localhost:8000/api/v1/health || echo "FAILED")
if echo "$API_HEALTH" | grep -q "healthy"; then
    echo "✓ API health check (direct) passed"
else
    echo "✗ API health check (direct) failed"
    echo "Response: $API_HEALTH"
fi

# Test Kong proxy
echo ""
echo "🌉 Testing Kong proxy..."
KONG_PROXY=$(curl -s http://localhost:8080/api/v1/health || echo "FAILED")
if echo "$KONG_PROXY" | grep -q "healthy"; then
    echo "✓ Kong proxy health check passed"
else
    echo "✗ Kong proxy health check failed"
    echo "Response: $KONG_PROXY"
fi

# Check database
echo ""
echo "🗄️  Testing database connection..."
DB_CHECK=$(docker compose exec -T db pg_isready -U kcardswap)
if echo "$DB_CHECK" | grep -q "accepting connections"; then
    echo "✓ Database is accepting connections"
else
    echo "✗ Database check failed"
fi

# Test CORS headers via Kong
echo ""
echo "🔒 Testing CORS headers..."
CORS_TEST=$(curl -s -I http://localhost:8080/api/v1/health | grep -i "access-control-allow-origin" || echo "")
if [ -n "$CORS_TEST" ]; then
    echo "✓ CORS headers are present"
else
    echo "⚠️  CORS headers not detected (may be normal)"
fi

echo ""
echo "✅ Setup verification complete!"
echo ""
echo "Access points:"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/api/v1/docs"
echo "  - Kong Gateway: http://localhost:8080"
echo "  - PostgreSQL: localhost:5432"
