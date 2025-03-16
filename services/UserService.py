from dto.req.UserReqDto import UserReqDto
from abc import ABC, abstractmethod


class UserService(ABC):

    @abstractmethod
    def get_users(self):
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int):
        pass

    @abstractmethod
    def get_user_by_email(self, email: str):
        pass

    @abstractmethod
    def get_user_by_username(self, username: str):
        pass

    @abstractmethod
    def get_user_by_multiple_filters(self, filters: list):
        pass

    @abstractmethod
    def add_user(self, user: UserReqDto):
        pass

    @abstractmethod
    def verify_email(self, user_id: int):
        pass

    @abstractmethod
    def reset_password(self, token: str, password: str):
        pass

    @abstractmethod
    def update_email(self, token: str, email: str):
        pass

    @abstractmethod
    def delete_user(self, user_id: int):
        pass
