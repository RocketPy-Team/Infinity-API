# RocketPy Infinity-API 

## Capabilities
- Performs rocket simulations
- Generates and store simulation hashes
- Generates and returns simulation reports

## Starting the server
- Dev: `uvicorn api:app --reload --port 3000`
- Prod: `gunicorn -k uvicorn.workers.UvicornWorker api:app --reload -b 0.0.0.0:3000`

## Testing

```
curl --location --request POST 'http://127.0.0.1:8000/env/' \
--header 'Content-Type: application/json' \
-d '{
    "latitude": 32.990254,
    "longitude": 106.974998
}'
```

## DOCS
- OpenAPI standard: `http://127.0.0.1:3000/redoc`
- Swagger UI: `http://127.0.0.1:3000/docs`
