## Smoke testing
### Create motor 
``` bash
curl --location --request POST 'http://127.0.0.1:3000/motor/' \
--header 'Content-Type: application/json' \
-d '{
    "burnOut": 3.9,
    "grainNumber": 5,
    "grainDensity": 1815,
    "grainOuterRadius": 0.033,
    "grainInitialInnerRadius": 0.015,
    "grainInitialHeight": 0.12,
    "grainsCenterOfMassPosition": -0.85704,
    "thrustSource": "lib/data/motors/Cesaroni_M1670.eng",
    "grainSeparation": 0.005,
    "nozzleRadius": 0.033,
    "throatRadius": 0.011,
    "interpolationMethod": "linear"
}'
```
### Read motor 
``` bash
curl -X 'GET' \
  'http://127.0.0.1:3000/motor/?motor_id=0' \
  -H 'accept: application/json'
```
## Read rocketpy motor 
``` bash
curl -X 'GET' \
  'http://127.0.0.1:3000/motor/rocketpy/?motor_id=0' \
  -H 'accept: application/json'
```
### Update motor 
``` bash
    curl -X 'PUT' \
        'http://127.0.0.1:3000/motor/?motor_id=0' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
-d '{
    "burnOut": 3.9,
    "grainNumber": 5,
    "grainDensity": 1615,
    "grainOuterRadius": 0.033,
    "grainInitialInnerRadius": 0.015,
    "grainInitialHeight": 0.12,
    "grainsCenterOfMassPosition": -0.85704,
    "thrustSource": "lib/data/motors/Cesaroni_M1670.eng",
    "grainSeparation": 0.005,
    "nozzleRadius": 0.033,
    "throatRadius": 0.011,
    "interpolationMethod": "linear"
}'
```
### Delete motor 
``` bash
curl -X 'DELETE' \
  'http://127.0.0.1:3000/motor/?motor_id=0' \
  -H 'accept: application/json'
```
### motor simulation
``` bash
curl -X 'GET' \
  'http://127.0.0.1:3000/motor/simulation/?motor_id=0' \
  -H 'accept: application/json'
```
