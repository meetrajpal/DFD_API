from pydantic import BaseModel


class LogoutResDto(BaseModel):
    details: str