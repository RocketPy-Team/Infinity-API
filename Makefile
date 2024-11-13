format: black flake8 pylint ruff

black:
	black ./lib || true
	black ./tests || true

flake8:
	flake8 --ignore E501,E402,F401,W503,C0414 ./lib || true
	flake8 --ignore E501,E402,F401,W503,C0414 ./tests || true

pylint:
	pylint --extension-pkg-whitelist='pydantic' ./lib || true
	pylint --extension-pkg-whitelist='pydantic' --disable=E0401,W0621 ./tests || true

ruff:
	ruff check --fix ./lib || true
	ruff check --fix ./tests || true

test:
	python3 -m pytest .

dev:
	python3 -m uvicorn lib:app --reload --port 3000

clean:
	docker stop infinity-api
	docker rm infinity-api
	docker system prune -fa

build:
	docker build -t infinity-api . --no-cache

.PHONY: black flake8 pylint test dev clean build ruff format
