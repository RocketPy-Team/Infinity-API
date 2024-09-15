black:
	black ./lib

lint: flake8 pylint

flake8:
	flake8 --ignore E501,E402,F401,W503 ./lib

pylint:
	pylint --extension-pkg-whitelist='pydantic' ./lib/*
