# Infinity-API

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/RocketPy-Team/Infinity-API)

## Capabilities
- Performs rocket simulations and returns simulation data
- Stores simulation input data in mongo-db

## Setup
- [Install python3](https://www.python.org/downloads/) 3.11.5 or above
- [install mongodb-atlas](https://www.mongodb.com/try/download/community)
- Install dependencies `python3 -m pip install -r requirements.txt`

## Development
- make format
- make test
- make clean
- make build

## Starting the server
- Setup MONGODB_CONNECTION_STRING:
```
$ touch .env && echo MONGODB_CONNECTION_STRING="$ConnectionString" > .env
```

### Docker
- run docker compose: `docker-compose up --build -d`

### Standalone 
- Dev: `python3 -m uvicorn src:app --reload --port 3000`
- Prod: `gunicorn -k uvicorn.workers.UvicornWorker src:app -b 0.0.0.0:3000`

## MCP Server
- The MCP bridge is mounted directly on the FastAPI app and is available at `/mcp` alongside the REST API.
- No extra process is required: `uvicorn src:app` serves both the REST routes and the MCP transport.

## Project structure
```
├── README.md    # this file
├── requirements.txt
│   
├── lib
│   │   
│   ├── api.py    # main app
│   │── secrets.py
│   │   
│   ├── controllers
│   │   ├── interface.py
│   │   ├── environment.py
│   │   ├── flight.py
│   │   ├── motor.py
│   │   └── rocket.py
│   │   
│   ├── services 
│   │   ├── environment.py
│   │   ├── flight.py
│   │   ├── motor.py
│   │   └── rocket.py
│   │   
│   ├── routes 
│   │   ├── environment.py
│   │   ├── flight.py
│   │   ├── motor.py
│   │   └── rocket.py
│   │   
│   ├── repositories
│   │   ├── interface.py
│   │   ├── environment.py
│   │   ├── flight.py
│   │   ├── motor.py
│   │   └── rocket.py
│   │   
│   ├── models
│   │   ├── interface.py
│   │   ├── environment.py
│   │   ├── flight.py
│   │   ├── motor.py
│   │   ├── rocket.py
│   │   │   
│   │   └── sub
│   │       ├── aerosurfaces.py
│   │       └── tanks.py
│   │   
│   └── views
│       ├── interface.py
│       ├── environment.py
│       ├── flight.py
│       ├── motor.py
│       └── rocket.py
│   
└── tests
```

## DOCS
- OpenAPI standard: [https://api.rocketpy.org/redoc](https://api.rocketpy.org/redoc)
- Swagger UI: [https://api.rocketpy.org/docs](https://api.rocketpy.org/docs)

## API Flowchart
General API workflow. Current available models are: Environment, Flight, Rocket and Motor.

### CRUD
```mermaid
sequenceDiagram
    participant User
    participant API
    participant MongoDB

    User ->> API: POST /model    
    API ->> MongoDB: Persist API Model as a document
    MongoDB -->> API: Model ID
    API -->> User: 201 ModelCreated View

    User ->> API: GET /model/:id
    API ->> MongoDB: Read API Model document
    MongoDB -->> API: API Model document
    API -->> User: 200 API ModelView

    User ->> API: PUT /model/:id
    API ->> MongoDB: Update API Model document
    API -->> User: 204

    User ->> API: DELETE /model/:id
    API ->> MongoDB: Delete API Model document
    MongoDB -->> API: Deletion Confirmation
    API -->> User: 204

```

### Simulating and extracting RocketPY native classes
```mermaid
sequenceDiagram
    participant User
    participant API
    participant MongoDB
    participant RocketPy lib

    User ->> API: GET model/:id/simulate/
    API -->> MongoDB: Retrieve API Model document
    MongoDB -->> API: API Model document 
    API ->> RocketPy: Initialize RocketPy native class and simulate
    RocketPy lib -->> API: Simulation Results
    API -->> User: Simulation Results

    User ->> API: GET /model/:id/rocketpy
    API -->> MongoDB: Retrieve API Model document
    MongoDB -->> API: API Model document 
    API ->> RocketPy: Initialize RocketPy native class
    RocketPy lib -->> API: RocketPy native class
    API -->> User: RocketPy native class as .dill binary (amd64)
```
