import datetime
from typing import Optional
from pydantic import BaseModel

class Env(BaseModel, frozen=True):
    latitude: float
    longitude: float
    rail_length: Optional[float] = 5.2
    elevation: Optional[int] = 1400
    atmospheric_model_type: Optional[str] = 'StandardAtmosphere'
    atmospheric_model_file: Optional[str] = 'GFS'
    date: Optional[datetime.datetime] = datetime.datetime.today() + datetime.timedelta(days=1)
