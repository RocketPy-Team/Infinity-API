## Smoke testing
### Create rocket 
``` bash
curl --location --request POST 'http://127.0.0.1:3000/rocket/' \
--header 'Content-Type: application/json' \
-d '{
    "radius": 0.0635,
    "mass": 16.241,
    "inertia": [6.6, 0.0351],
    "powerOffDrag": "lib/data/calisto/powerOffDragCurve.csv",
    "powerOnDrag": "lib/data/calisto/powerOnDragCurve.csv",
    "center_of_mass_without_motor": 0,
    "coordinate_system_orientation": "tail_to_nose",
    "motor_position": -1.255,
    "rail_buttons": {
      "distanceToCM": [
        0.2,
        -0.5
      ],
      "angularPosition": 45
    },
    "motor": {
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
    },
    "nose": {
      "length": 0.55829,
      "kind": "vonKarman",
      "position": 1.278,
      "baseRadius": 0.0635,
      "rocketRadius": 0.0635
    },
    "fins": {
      "n": 4,
      "rootChord": 0.12,
      "tipChord": 0.04,
      "span": 0.1,
      "position": -1.04956,
      "cantAngle": 0,
      "radius": 0.0635,
      "airfoil": ""
    },
    "tail": {
      "topRadius": 0.0635,
      "bottomRadius": 0.0435,
      "length": 0.06,
      "position": -1.194656,
      "radius": 0.0635
    },
    "parachutes": {
      "name": [
        "Main",
        "Drogue"
      ],
      "CdS": [
        10,
        1
      ],
      "samplingRate": [
        105,
        105
      ],
      "lag": [
        1.5,
        1.5
      ],
      "noise": [
        [
          0,
          8.3,
          0.5
        ],
        [
          0,
          8.3,
          0.5
        ]
      ],
      "triggers": [
        "lambda p, h, y: y[5] < 0 and h < 800",
        "lambda p, h, y: y[5] < 0"
      ]
    }
}'
```
### Read rocket 
``` bash
curl -X 'GET' \
  'http://127.0.0.1:3000/rocket/?rocket_id=0' \
  -H 'accept: application/json'
```
## Read rocketpy rocket 
``` bash
curl -X 'GET' \
  'http://127.0.0.1:3000/rocket/rocketpy/?rocket_id=0' \
  -H 'accept: application/json'
```
### Update rocket 
``` bash
    curl -X 'PUT' \
        'http://127.0.0.1:3000/rocket/?rocket_id=0' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
-d '{
    "radius": 0.0635,
    "mass": 17.241,
    "inertia": [ 6.6, 0.0351 ],
    "powerOffDrag": "lib/data/calisto/powerOffDragCurve.csv",
    "powerOnDrag": "lib/data/calisto/powerOnDragCurve.csv",
    "center_of_mass_without_motor": 0,
    "coordinate_system_orientation": "tail_to_nose",
    "motor_position": -1.255,
    "rail_buttons": {
      "distanceToCM": [
        0.2,
        -0.5
      ],
      "angularPosition": 45
    },
    "motor": {
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
    },
    "nose": {
      "length": 0.55829,
      "kind": "vonKarman",
      "position": 1.278,
      "baseRadius": 0.0635,
      "rocketRadius": 0.0635
    },
    "fins": {
      "n": 4,
      "rootChord": 0.12,
      "tipChord": 0.04,
      "span": 0.1,
      "position": -1.04956,
      "cantAngle": 0,
      "radius": 0.0635,
      "airfoil": ""
    },
    "tail": {
      "topRadius": 0.0635,
      "bottomRadius": 0.0435,
      "length": 0.06,
      "position": -1.194656,
      "radius": 0.0635
    },
    "parachutes": {
      "name": [
        "Main",
        "Drogue"
      ],
      "CdS": [
        10,
        1
      ],
      "samplingRate": [
        105,
        105
      ],
      "lag": [
        1.5,
        1.5
      ],
      "noise": [
        [
          0,
          8.3,
          0.5
        ],
        [
          0,
          8.3,
          0.5
        ]
      ],
      "triggers": [
        "lambda p, h, y: y[5] < 0 and h < 800",
        "lambda p, h, y: y[5] < 0"
      ]
    }
}'
```
### Delete rocket 
``` bash
curl -X 'DELETE' \
  'http://127.0.0.1:3000/rocket/?rocket_id=0' \
  -H 'accept: application/json'
```
### Rocket simulation
``` bash
curl -X 'GET' \
  'http://127.0.0.1:3000/rocket/simulation/?rocket_id=0' \
  -H 'accept: application/json'
```
