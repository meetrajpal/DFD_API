from typing import Any
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from config.database import Base


class Prediction(Base):
    __tablename__ = 'prediction'
    pred_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey('user.user_id', ondelete="CASCADE"), nullable=False)
    video_id = Column(Integer, ForeignKey("video.video_id", ondelete="CASCADE"),  nullable=False)
    pred_label = Column(String, nullable=False)
    user = relationship('User', back_populates='predictions')
    video = relationship("Video", back_populates="prediction", cascade="all, delete")

    def __init__(self, user_id, video_id, pred_label, **kw: Any):
        super().__init__(**kw)
        self.user_id = user_id
        self.video_id = video_id
        self.pred_label = pred_label
