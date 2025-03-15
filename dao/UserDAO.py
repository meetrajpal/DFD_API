from operator import and_
from sqlalchemy import update
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import user
from models.User import User


class UserDAO:
    def __init__(self, db: Session):
        self.db = db

    def get_all_users(self):
        return self.db.query(User).all()

    def get_user_by_id(self, user_id: int):
        return self.db.query(User).filter(User.user_id == user_id).first()

    def get_user_by_username(self, username: str):
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_multiple_filters(self, filters: list):
        return self.db.query(User).filter(and_(*filters)).all()

    def create_user(self, user: User):
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def verify_user_email(self, user_id: int):
        stmt = update(User).where(User.user_id == user_id).values({"verified_email": True})
        result = self.db.execute(stmt)
        self.db.commit()
        return int(result.rowcount) > 0

    def update_user_email(self, user_id: int, email: str):
        stmt = update(User).where(User.user_id == user_id).values({"email": email, "verified_email": False})
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount > 0

    def delete_user(self, user: User):
        # self.db.query(User).filter(User.user_id == user_id).delete()
        self.db.delete(user)
        self.db.commit()
