from pydantic import BaseModel


class VideoResDto(BaseModel):
    video_id: int
    user_id: int
    filename: str
    filepath: str
