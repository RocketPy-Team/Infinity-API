from pydantic import BaseModel
from typing import Optional
import datetime

class Env(BaseModel, frozen=True):
    latitude: float 
    longitude: float
    railLength: Optional[float] = 5.2
    elevation: Optional[int] = 1400
    atmosphericModelType: Optional[str] = 'StandardAtmosphere' 
    atmosphericModelFile: Optional[str] = 'GFS'
    date: Optional[datetime.datetime] = datetime.datetime.today() + datetime.timedelta(days=1) 
