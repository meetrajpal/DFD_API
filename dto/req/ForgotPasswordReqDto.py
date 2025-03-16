from pydantic import BaseModel


class ForgotPasswordReqDto(BaseModel):
    email: str