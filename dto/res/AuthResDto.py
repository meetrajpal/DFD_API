from pydantic import BaseModel


class AuthResDto(BaseModel):
    access_token: str
    token_type: str
