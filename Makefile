pre-commit: format lint test

lint:
	poetry run flake8 .
	poetry run mypy kuqueue

test:
	poetry run pytest

format:
	poetry run black .
	poetry run isort .

watch:
	poetry run ptw . -- -vvv
