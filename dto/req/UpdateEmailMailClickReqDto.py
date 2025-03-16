from pydantic import BaseModel


class UpdateEmailMailClickReqDto(BaseModel):
    email: str
