from typing import Any
from sqlalchemy import Column, Integer, ForeignKey, String
from config.database import Base


class Frame(Base):
    __tablename__ = 'frame'
    frame_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    video_id = Column(Integer, ForeignKey("video.video_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)

    def __init__(self, video_id, user_id, filename, filepath, **kw: Any):
        super().__init__(**kw)
        self.video_id = video_id
        self.user_id = user_id
        self.filename = filename
        self.filepath = filepath
