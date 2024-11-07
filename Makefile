format: flake8 pylint ruff black

black:
	black ./lib && black ./tests

flake8:
	flake8 --ignore E501,E402,F401,W503,C0414 ./lib && flake8 --ignore E501,E402,F401,W503,C0414 ./tests

pylint:
	pylint --extension-pkg-whitelist='pydantic' ./lib && pylint --extension-pkg-whitelist='pydantic' ./tests

ruff:
	ruff check --fix

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
