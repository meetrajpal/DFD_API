from pydantic import BaseModel


class FrameReqDto(BaseModel):
    video_id: int
    filename: str
    filepath: str
