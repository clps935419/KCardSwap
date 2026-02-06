#!/usr/bin/env bash
set -euo pipefail

# Simple GCE deployment helper for this repo.
# Assumes the repo is already on the VM and DNS/firewall are configured.

REPO_DIR=${REPO_DIR:-"/opt/kcardswap"}

if ! command -v docker >/dev/null 2>&1; then
  echo "Installing Docker..."
  curl -fsSL https://get.docker.com | sh
  sudo usermod -aG docker "$USER"
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "Installing Docker Compose plugin..."
  sudo apt-get update -y
  sudo apt-get install -y docker-compose-plugin
fi

if [[ ! -d "$REPO_DIR" ]]; then
  echo "Repo directory not found: $REPO_DIR"
  echo "Set REPO_DIR or clone the repo first."
  exit 1
fi

cd "$REPO_DIR"

if [[ ! -f .env.prod ]]; then
  echo "Creating .env.prod from .env.prod.example"
  cp .env.prod.example .env.prod
  echo "Please edit .env.prod before running in production."
fi

echo "Building and starting production services..."
make prod-up

echo "Deployment complete."
