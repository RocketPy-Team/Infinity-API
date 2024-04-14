import datetime
from typing import Optional
from pydantic import BaseModel


class Env(BaseModel, frozen=True):
    latitude: float = 0
    longitude: float = 0
    elevation: Optional[int] = 1400

    # Opional parameters
    atmospheric_model_type: Optional[str] = "standard_atmosphere"
    atmospheric_model_file: Optional[str] = "GFS"
    date: Optional[datetime.datetime] = (
        datetime.datetime.today() + datetime.timedelta(days=1)
    )
