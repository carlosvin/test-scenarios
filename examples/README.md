# pytest-scenarios demo

This folder contains the runnable example used in the article [Isolated Integration Tests with pytest-scenarios](https://carlosvin.github.io/pytest-scenarios-isolated-integration-tests)

## Requirements

- [uv](https://github.com/astral-sh/uv) 0.4 or newer
- Docker (to spin up a disposable MongoDB instance)

## Getting started

```bash
# within examples dir

uv sync

docker run --rm --name mongo-test -p 27017:27017 -d mongo:8

uv run pytest tests/integration -q
```

The pytest plugin cleans up collections before every test, so each scenario remains isolated even when tests fail.
