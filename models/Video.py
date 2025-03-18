from typing import Any
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from config.database import Base


class Video(Base):
    __tablename__ = 'video'
    video_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    user = relationship("User", back_populates="videos")

    def __init__(self, user_id, filename, filepath, **kw: Any):
        super().__init__(**kw)
        self.user_id = user_id
        self.filename = filename
        self.filepath = filepath
