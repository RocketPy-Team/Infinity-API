import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel


class AtmosphericModelTypes(str, Enum):
    STANDARD_ATMOSPHERE: str = "STANDARD_ATMOSPHERE"
    CUSTOM_ATMOSPHERE: str = "CUSTOM_ATMOSPHERE"
    WYOMING_SOUNDING: str = "WYOMING_SOUNDING"
    NOAARUCSOUNDING: str = "NOAARUCSOUNDING"
    FORECAST: str = "FORECAST"
    REANALYSIS: str = "REANALYSIS"
    ENSEMBLE: str = "ENSEMBLE"


class Env(BaseModel):
    latitude: float
    longitude: float
    elevation: Optional[int] = None

    # Optional parameters
    atmospheric_model_type: Optional[AtmosphericModelTypes] = None
    atmospheric_model_file: Optional[str] = None
    date: Optional[datetime.datetime] = (
        datetime.datetime.today() + datetime.timedelta(days=1)
    )
