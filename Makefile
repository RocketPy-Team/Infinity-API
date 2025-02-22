format: black ruff
lint: flake8 pylint

black:
	black ./src || true
	black ./tests || true

flake8:
	flake8 --ignore E501,E402,F401,W503,C0414 ./src || true
	flake8 --ignore E501,E402,F401,W503,C0414 ./tests || true

pylint:
	pylint ./src || true
	pylint ./tests || true

ruff:
	ruff check --fix ./src || true
	ruff check --fix ./tests || true

test:
	python3 -m pytest .

dev:
	python3 -m uvicorn src:app --reload --port 3000

clean:
	docker stop infinity-api
	docker rm infinity-api
	docker system prune -fa

build:
	docker build -t infinity-api . --no-cache

.PHONY: black flake8 pylint test dev clean build ruff format
