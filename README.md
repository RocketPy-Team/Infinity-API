# Infinity-API

## Capabilities
- Performs rocket simulations and returns simulation data
- Stores simulation input data in mongo-db

## Setup
- [Install python3](https://www.python.org/downloads/) 3.11.5 or above
- [install mongodb-atlas](https://www.mongodb.com/try/download/community)
- Install dependencies `python3 -m pip install -r requirements.txt`

## Starting the server
- Setup MONGODB_CONNECTION_STRING:
```
$ touch .env && echo MONGODB_CONNECTION_STRING="$ConnectionString" > .env
```

### Docker
- run docker compose: `docker-compose up --build -d`

### Standard
- Dev: `python3 -m uvicorn lib:app --reload --port 3000`
- Prod: `gunicorn -k uvicorn.workers.UvicornWorker lib:app -b 0.0.0.0:3000`

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
│   │   ├── repo.py
│   │   ├── environment.py
│   │   ├── flight.py
│   │   ├── motor.py
│   │   └── rocket.py
│   │   
│   ├── models
│   │   ├── aerosurfaces.py
│   │   ├── environment.py
│   │   ├── flight.py
│   │   ├── motor.py
│   │   ├── parachute.py
│   │   └── rocket.py
│   │   
│   └── views
│       ├── environment.py
│       ├── flight.py
│       ├── motor.py
│       └── rocket.py
│   
└── tests
    ├── infinity-api-postman-collection.json
    │   
    ├── integration 
    │   
    └── unit
        ├── test_secrets.py
        ├── test_api.py
        │   
        ├── test_controllers
        │   ├── test_environment.py
        │   ├── test_flight.py
        │   ├── test_motor.py
        │   └── test_rocket.py
        │
        ├── test_routes
        │   ├── test_environment.py
        │   ├── test_flight.py
        │   ├── test_motor.py
        │   └── test_rocket.py
        │
        ├── test_repositories
        │   ├── test_environment.py
        │   ├── test_flight.py
        │   ├── test_motor.py
        │   └── test_rocket.py
        │
        ├── test_models
        │   ├── test_environment.py
        │   ├── test_flight.py
        │   ├── test_motor.py
        │   └── test_rocket.py
        │   
        └── test_views
            ├── test_environment.py
            ├── test_flight.py
            ├── test_motor.py
            └── test_rocket.py
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

    User ->> API: POST /rocketpy-model    
    API ->> MongoDB: Persist Rocketpy Model
    MongoDB -->> API: Model ID
    API -->> User: Model ID

    User ->> API: GET /rocketpy-model/:id
    API ->> MongoDB: Retrieve Rocketpy Model
    MongoDB -->> API: Rocketpy Model
    API -->> User: Rocketpy Model

    User ->> API: PUT /rocketpy-model/:id
    API ->> MongoDB: Update Rocketpy Model
    MongoDB -->> API: Updated Model
    API -->> User: Updated Model

    User ->> API: DELETE /rocketpy-model/:id
    API ->> MongoDB: Delete Rocketpy Model
    MongoDB -->> API: Deletion Confirmation
    API -->> User: Deletion Confirmation

```

### Simulating and extracting RocketPY native class 
```mermaid
sequenceDiagram
    participant User
    participant API
    participant MongoDB
    participant Rocketpy lib

    User ->> API: POST /simulate/rocketpy-model/:id
    API -->> MongoDB: Retrieve Rocketpy Model
    MongoDB -->> API: Rocketpy Model
    API ->> Rocketpy lib: Simulate Rocketpy Model
    Rocketpy lib -->> API:  Simulation Results
    API -->> User: Simulation Results

    User ->> API: POST /rocketpy/rocketpy-model/:id
    API -->> MongoDB: Retrieve Rocketpy Model
    MongoDB -->> API: Rocketpy Model
    API ->> Rocketpy lib: Rocketpy Model
    Rocketpy lib -->> API:  Rocketpy native class as json pickle string
    API -->> User: Rocketpy native class as json pickle string
```
