from pydantic import BaseModel


class FrameResDto(BaseModel):
    frame_id: int
    video_id: int
    user_id: int
    filename: str
    filepath: str
