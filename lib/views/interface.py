from pydantic import BaseModel


class ApiBaseView(BaseModel):
    message: str = 'View not implemented'
