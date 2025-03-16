from pydantic import BaseModel


class ForgotPasswordMailClickReqDto(BaseModel):
    password: str
    cnf_password: str
