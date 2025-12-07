.PHONY: install test test-update coverage lint format upgrade build

# Install Python and project dependencies
install:
	uv python install
	uv sync --locked --all-extras --dev

# Run tests
test:
	uv run pytest tests

# Run tests and update snapshots
test-update:
	uv run pytest tests --snapshot-update

# Generate coverage report
coverage:
	uv run pytest --cov-report html --junitxml=junit.xml -o junit_family=legacy --cov=src --cov-report=term-missing tests/

# Lint code
lint:
	uv run ruff check

# Format code
format:
	uv run ruff check --fix

# Upgrade all dependencies
upgrade:
	uv sync --upgrade

build:
	uv build