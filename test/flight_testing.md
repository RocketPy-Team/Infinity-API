## Smoke testing
### Create flight
``` bash
curl --location --request POST 'http://127.0.0.1:3000/flight/' \
--header 'Content-Type: application/json' \
-d '{
  "environment": {
    "latitude": 0,
    "longitude": 0,
    "railLength": 5.2,
    "elevation": 1400,
    "atmosphericModelType": "StandardAtmosphere",
    "atmosphericModelFile": "GFS",
    "date": "2023-05-09T16:30:50.065992"
  },
  "rocket": {
    "radius": 0.0635,
    "mass": 16.241,
    "inertiaI": 6.6,
    "inertiaZ": 0.0351,
    "powerOffDrag": "lib/data/calisto/powerOffDragCurve.csv",
    "powerOnDrag": "lib/data/calisto/powerOnDragCurve.csv",
    "centerOfDryMassPosition": 0,
    "coordinateSystemOrientation": "tailToNose",
    "motorPosition": -1.255,
    "railButtons": {
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
  },
  "inclination": 85,
  "heading": 0
}'
```
### Read flight
``` bash
curl -X 'GET' \
  'http://127.0.0.1:3000/flight/?flight_id=0' \
  -H 'accept: application/json'
```
## Read rocketpy flight
``` bash
curl -X 'GET' \
  'http://127.0.0.1:3000/flight/rocketpy/?flight_id=0' \
  -H 'accept: application/json'
```
### Update flight
``` bash
    curl -X 'PUT' \
        'http://127.0.0.1:3000/flight/?flight_id=0' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
-d '{
  "environment": {
    "latitude": 0,
    "longitude": 0,
    "railLength": 5.2,
    "elevation": 1400,
    "atmosphericModelType": "StandardAtmosphere",
    "atmosphericModelFile": "GFS",
    "date": "2023-05-09T16:30:50.065992"
  },
  "rocket": {
    "radius": 0.0635,
    "mass": 16.241,
    "inertiaI": 6.6,
    "inertiaZ": 0.0351,
    "powerOffDrag": "lib/data/calisto/powerOffDragCurve.csv",
    "powerOnDrag": "lib/data/calisto/powerOnDragCurve.csv",
    "centerOfDryMassPosition": 0,
    "coordinateSystemOrientation": "tailToNose",
    "motorPosition": -1.255,
    "railButtons": {
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
  },
  "inclination": 85,
  "heading": 0
}'
```

### Delete flight
``` bash
curl -X 'DELETE' \
  'http://127.0.0.1:3000/flight/?flight_id=0' \
  -H 'accept: application/json'
```

### Flight Simulation
``` bash
curl -X 'GET' \
  'http://127.0.0.1:3000/flight/simulation/?flight_id=0' \
  -H 'accept: application/json'
```
