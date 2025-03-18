from pydantic import BaseModel


class UnauthenticatedResDto(BaseModel):
    details: str
