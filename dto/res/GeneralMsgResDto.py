from typing import Any

from .ErrorResDto import ErrorResDto
from pydantic import BaseModel


class GeneralMsgResDto(BaseModel):
    isSuccess: bool
    hasException: bool
    errorResDto: ErrorResDto | None = None
    message: str | None = None
