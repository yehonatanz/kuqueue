SRC         = kuqueue
COV_OPTIONS = --cov $(SRC) --cov-report term

pre-commit: format lint test

lint:
	poetry run flake8 .
	poetry run mypy $(SRC)

test:
	poetry run pytest $(COV_OPTIONS) --cov-report xml:junit.xml

format:
	poetry run black .
	poetry run isort .

watch:
	poetry run ptw . -- -vvv $(COV_OPTIONS) --cov-report html
