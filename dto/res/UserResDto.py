from pydantic import BaseModel


class UserResDto(BaseModel):
    user_id: int
    username: str
    name: str
    email: str
    password: str
    verified_email: bool
