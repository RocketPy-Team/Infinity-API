# RocketPy Infinity-API 

## Capabilities
- Performs rocket simulations and returns simulation data
- Stores simulation data in mongo-db

## Setup
- [Install python3](https://www.python.org/downloads/)
- Install dependencies `python3 -m pip install -r requirements.txt`

## Starting the server
- Dev: `uvicorn lib:app --reload --port 3000`
- Prod: `gunicorn -k uvicorn.workers.UvicornWorker lib:app --reload -b 0.0.0.0:3000`

## Smoke testing
``` bash
curl --location --request POST 'http://127.0.0.1:3000/simulation/env/' \
--header 'Content-Type: application/json' \
-d '{
    "latitude": 32.990254,
    "longitude": 106.974998
}'
```

## Project structure
```
├── README.md
├── apprunner.yaml    # AWS App runner config
├── lib
│   ├── __init__.py
│   ├── __main__.py
│   ├── __pycache__
│   ├── api.py        # main app
│   ├── controllers.py
│   ├── models.py
│   ├── views.py
│   └── data.py       # extra simulation dependencies
└── requirements.txt
```

## DOCS
- OpenAPI standard: `http://127.0.0.1:3000/redoc`
- Swagger UI: `http://127.0.0.1:3000/docs`
