from rocketpy import Rocket, SolidMotor
from pydantic import BaseModel
from typing import Optional, TypeVar
import datetime

# pydantic models
class Env(BaseModel):
    latitude: float 
    longitude: float
    railLength: Optional[float] = 5.2
    elevation: Optional[int] = 1400
    atmosphericModelType: Optional[str] = 'StandardAtmosphere' 
    atmosphericModelFile: Optional[str] = 'GFS'
    date: Optional[datetime.datetime] = datetime.datetime.today() + datetime.timedelta(days=1) 

class Flight(BaseModel):
    environment: TypeVar('Environment')
    rocket: Optional[TypeVar('Rocket')]
    inclination: Optional[int] = 85
    heading: Optional[int] = 0

# non-pydantic models
class Calisto(Rocket):
    def __init__(self):
        super().__init__(
                motor=Pro75M1670(),
                radius=127/2000,
                mass=19.197-2.956,
                inertiaI=6.60,
                inertiaZ=0.0351,
                distanceRocketNozzle=-1.255,
                distanceRocketPropellant=-0.85704,
                powerOffDrag='lib/data/calisto/powerOffDragCurve.csv',
                powerOnDrag='lib/data/calisto/powerOnDragCurve.csv'
        )
        self.setRailButtons([0.2, -0.5])
        self.addNose(length=0.55829, kind="vonKarman", distanceToCM=0.71971)
        self.addTrapezoidalFins(4, span=0.100, rootChord=0.120, tipChord=0.040, distanceToCM=-1.04956)
        self.addTail(topRadius=0.0635, bottomRadius=0.0435, length=0.060, distanceToCM=-1.194656)
        self.addParachute('Main',
                            CdS=10.0,
                            trigger=self.mainTrigger,
                            samplingRate=105,
                            lag=1.5,
                            noise=(0, 8.3, 0.5))
        self.addParachute('Drogue',
                              CdS=1.0,
                              trigger=self.drogueTrigger,
                              samplingRate=105,
                              lag=1.5,
                              noise=(0, 8.3, 0.5))

    def drogueTrigger(self, p, y):
        return True if y[5] < 0 else False

    def mainTrigger(self, p, y):
        return True if y[5] < 0 and y[2] < 800 else False

class Pro75M1670(SolidMotor):
    def __init__(self):
        super().__init__(
                burnOut=3.9,
                grainNumber=5,
                grainDensity=1815,
                grainOuterRadius=33/1000,
                grainInitialInnerRadius=15/1000,
                grainInitialHeight=120/1000,
                thrustSource = "lib/data/motors/Cesaroni_M1670.eng"
        )
        self.grainSeparation = 5/1000
        self.nozzleRadius = 33/1000
        self.throatRadius = 11/1000
        self.interpolationMethod = 'linear'
