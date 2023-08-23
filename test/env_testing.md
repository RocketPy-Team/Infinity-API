## Smoke testing
### Create environment 
``` bash
curl --location --request POST 'http://127.0.0.1:3000/env/' \
--header 'Content-Type: application/json' \
-d '{
    "latitude": 0,
    "longitude": 0,
    "elevation": 1400,
    "atmospheric_model_type": "standard_atmosphere",
    "atmospheric_model_file": "GFS",
    "date": "2023-05-09T16:30:50.065992"
  }'
```
### Read environment 
``` bash
curl -X 'GET' \
  'http://127.0.0.1:3000/env/?env_id=0' \
  -H 'accept: application/json'
```
## Read rocketpy environment 
``` bash
curl -X 'GET' \
  'http://127.0.0.1:3000/env/rocketpy/?env_id=0' \
  -H 'accept: application/json'
```
### Update environment 
``` bash
    curl -X 'PUT' \
        'http://127.0.0.1:3000/env/?env_id=0' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
-d '{
    "latitude": 0,
    "longitude": 0,
    "elevation": 1400,
    "atmospheric_model_type": "standard_atmosphere",
    "atmospheric_model_file": "GFS",
    "date": "2023-05-09T16:30:50.065992"
  }'
```
### Delete environment 
``` bash
curl -X 'DELETE' \
  'http://127.0.0.1:3000/env/?env_id=0' \
  -H 'accept: application/json'
```
### Environment simulation
``` bash
curl -X 'GET' \
  'http://127.0.0.1:3000/env/simulate/?env_id=0' \
  -H 'accept: application/json'
```
