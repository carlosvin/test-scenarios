.PHONY: install test test-update coverage lint format upgrade

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
	uv run pytest --cov-report html --cov-report xml --cov=src/pytest_scenarios --cov-report=term-missing tests

# Lint code
lint:
	uv run ruff check

# Format code
format:
	uv run ruff check --fix

# Upgrade all dependencies
upgrade:
	uv sync --upgrade
