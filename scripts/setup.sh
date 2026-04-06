#!/usr/bin/env bash
set -euo pipefail

PROJECT="reportgenerator"
echo "==> Setting up $PROJECT"

# 1. Check Python
if ! command -v python3 &>/dev/null; then
  echo "ERROR: python3 not found" >&2; exit 1
fi

# 2. Create virtual environment
echo "==> Creating virtual environment"
python3 -m venv .venv
source .venv/bin/activate

# 3. Upgrade pip & install deps
echo "==> Installing dependencies"
pip install --upgrade pip -q
pip install -e ".[dev]" -q

# 4. Copy .env.example if .env missing
if [ ! -f .env ]; then
  cp .env.example .env
  echo "==> .env created from .env.example — edit before running!"
fi

# 5. Wait for postgres
echo "==> Waiting for database..."
for i in $(seq 1 15); do
  python3 -c "import psycopg2, os; psycopg2.connect(os.environ.get('DATABASE_URL','postgresql://localhost/app'))" 2>/dev/null && break
  echo "  attempt $i/15..."
  sleep 2
done

# 6. Run migrations
echo "==> Running migrations"
alembic upgrade head

# 7. Seed database
echo "==> Seeding database"
python3 -m src.cli.seed

echo ""
echo "==> reportgenerator is ready!"
echo "    Activate env : source .venv/bin/activate"
echo "    Start server : make dev"
echo "    API docs     : http://localhost:8000/docs"
