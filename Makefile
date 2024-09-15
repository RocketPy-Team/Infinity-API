black:
	black ./lib

lint: flake8 pylint

flake8:
	flake8 --ignore E501,E402,F401,W503 ./lib

pylint:
	pylint --extension-pkg-whitelist='pydantic' ./lib/*

dev:
	python3 -m uvicorn lib:app --reload --port 3000

clean:
	docker stop infinity-api
	docker rm infinity-api
	docker system prune -fa

build:
	docker build -t infinity-api . --no-cache
