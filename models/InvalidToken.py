from typing import Any
from sqlalchemy import Column, Integer, String
from config.database import Base


class InvalidToken(Base):
    __tablename__ = 'invalid token'
    token_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    token = Column(String, unique=True, nullable=False)

    def __init__(self, token, **kw: Any):
        super().__init__(**kw)
        self.token = token
