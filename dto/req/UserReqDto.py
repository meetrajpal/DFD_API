from pydantic import BaseModel


class UserReqDto(BaseModel):
    username: str
    name: str
    email: str
    password: str
    cnf_password: str
