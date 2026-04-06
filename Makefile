# reportgenerator — Developer Makefile
.PHONY: dev test lint format migrate docker-up docker-down clean

dev:  ## Start development server with hot-reload
	uvicorn src.main:app --reload --port 8000

test:  ## Run test suite
	pytest tests/ -v --tb=short

test-cov:  ## Run tests with coverage report
	pytest tests/ --cov=src --cov-report=term-missing --cov-report=html

lint:  ## Lint with ruff
	ruff check .

format:  ## Format code
	ruff format .

migrate:  ## Run database migrations
	alembic upgrade head

migrate-new:  ## Create new migration (usage: make migrate-new MSG="add users table")
	alembic revision --autogenerate -m "$(MSG)"

install:  ## Install all dependencies
	pip install -e ".[dev]"

docker-up:  ## Start all services
	docker compose up -d

docker-down:  ## Stop all services
	docker compose down

docker-build:  ## Rebuild Docker image
	docker compose build --no-cache

clean:  ## Clean build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true
	find . -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage

help:  ## Show available targets
	@grep -E "^[a-zA-Z_-]+:.*##" $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
