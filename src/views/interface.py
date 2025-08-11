from pydantic import BaseModel, ConfigDict


class ApiBaseView(BaseModel):
    message: str = 'View not implemented'
    model_config = ConfigDict(ser_json_exclude_none=True)
