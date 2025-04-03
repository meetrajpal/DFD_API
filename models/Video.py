from typing import Any
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from config.database import Base


class Video(Base):
    __tablename__ = 'video'
    video_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    source = Column(String, nullable=False)
    url = Column(String, nullable=True)
    user = relationship("User", back_populates="videos")
    prediction = relationship("Prediction", back_populates="video", cascade="all, delete")

    def __init__(self, user_id, filename, filepath, source, url, **kw: Any):
        super().__init__(**kw)
        self.user_id = user_id
        self.filename = filename
        self.filepath = filepath
        self.source = source
        self.url = url
