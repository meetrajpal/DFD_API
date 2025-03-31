from typing import Any
from sqlalchemy import Column, Integer, Boolean, String
from sqlalchemy.orm import relationship
from config.database import Base


class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    verified_email = Column(Boolean, default=False, nullable=False)
    videos = relationship("Video", back_populates="user")
    predictions = relationship("Prediction", back_populates="user")

    def __init__(self, username, name, email, password, **kw: Any):
        super().__init__(**kw)
        self.username = username
        self.name = name
        self.email = email
        self.password = password
        self.verified_email = False
