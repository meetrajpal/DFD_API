from pydantic import BaseModel


class AuthReqDto(BaseModel):
    username_or_email: str
    password: str
