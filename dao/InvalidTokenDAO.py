from sqlalchemy.orm import Session
from models.InvalidToken import InvalidToken


class InvalidTokenDAO:
    def __init__(self, db: Session):
        self.db = db

    def get_invalid_token_by_id(self, token_id: int):
        return self.db.query(InvalidToken).filter(InvalidToken.token_id == token_id).first()

    def get_invalid_token_by_token(self, token: str):
        return self.db.query(InvalidToken).filter(InvalidToken.token == token).first()

    def expire_token(self, token: InvalidToken):
        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)
        return token
