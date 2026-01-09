from pydantic import BaseModel, ConfigDict


class ApiBaseView(BaseModel):
    message: str = 'View not implemented'
    model_config = ConfigDict(ser_json_exclude_none=True)


class PaginatedResponse(ApiBaseView):
    items: list
    total: int
    skip: int
    limit: int
