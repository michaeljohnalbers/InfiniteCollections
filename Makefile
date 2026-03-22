.PHONY: typecheck lint lint-check format test full-lint

full-lint: typecheck lint format

typecheck:
	uv run mypy .
lint:
	uv run ruff check . --fix
lint-check:
	uv run ruff check .
format:
	uv run ruff format .
test:
	uv run pytest
