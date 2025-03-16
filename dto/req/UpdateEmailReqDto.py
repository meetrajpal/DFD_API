from pydantic import BaseModel


class UpdateEmailReqDto(BaseModel):
    email: str
