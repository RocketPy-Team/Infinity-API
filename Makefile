VENV_BIN ?= ./infinity_env/bin
PYLINTHOME ?= .pylint.d

export PYLINTHOME

ifneq (,$(wildcard $(VENV_BIN)/black))
BLACK := $(VENV_BIN)/black
else
BLACK := black
endif

ifneq (,$(wildcard $(VENV_BIN)/ruff))
RUFF := $(VENV_BIN)/ruff
else
RUFF := ruff
endif

ifneq (,$(wildcard $(VENV_BIN)/flake8))
FLAKE8 := $(VENV_BIN)/flake8
else
FLAKE8 := flake8
endif

ifneq (,$(wildcard $(VENV_BIN)/pylint))
PYLINT := $(VENV_BIN)/pylint
else
PYLINT := pylint
endif

ifneq (,$(wildcard $(VENV_BIN)/pytest))
PYTEST := $(VENV_BIN)/pytest
else
PYTEST := python3 -m pytest
endif

ifneq (,$(wildcard $(VENV_BIN)/uvicorn))
UVICORN := $(VENV_BIN)/uvicorn
else
UVICORN := python3 -m uvicorn
endif

format: black ruff
lint: flake8 pylint

black:
	$(BLACK) ./src || true
	$(BLACK) ./tests || true

flake8:
	$(FLAKE8) --ignore E501,E402,F401,W503,C0414 ./src || true
	$(FLAKE8) --ignore E501,E402,F401,W503,C0414 ./tests || true

pylint:
	@mkdir -p $(PYLINTHOME)
	$(PYLINT) ./src || true
	$(PYLINT) ./tests || true

ruff:
	$(RUFF) check --fix ./src || true
	$(RUFF) check --fix ./tests || true

test:
	$(PYTEST) .

dev:
	$(UVICORN) src:app --reload --port 3000 --loop uvloop

clean:
	docker stop infinity-api
	docker rm infinity-api
	docker system prune -fa

build:
	docker build -t infinity-api . --no-cache

.PHONY: black flake8 pylint test dev clean build ruff format
