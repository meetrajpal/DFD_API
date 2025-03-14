from pydantic import BaseModel


class ErrorResDto(BaseModel):
    code: str
    message: str
    details: str
