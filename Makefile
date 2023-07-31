PORT ?= 8000

install:
	poetry install

lint:
	poetry run flake8

test:
	poetry run pytest -vv

check: test lint

dev:
	poetry run flask --app page_analyzer:app run

start:
	poetry run gunicorn -w 4 -b 0.0.0.0:$(PORT) page_analyzer:app

.env:
	@test ! -f .env && cp .env.example .env

clear-db:
	cat database.sql | psql flask_db
