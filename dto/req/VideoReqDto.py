from typing import Any

from pydantic import BaseModel


class VideoReqDto(BaseModel):
    filename: str
    filepath: str


