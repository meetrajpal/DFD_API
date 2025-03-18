from abc import ABC, abstractmethod
from dto.req.AuthReqDto import AuthReqDto


class AuthService(ABC):

    @abstractmethod
    def login(self, creds: AuthReqDto):
        pass

    @abstractmethod
    def logout(self, token: str):
        pass

    @abstractmethod
    def forgot_password(self, email: str):
        pass

    @abstractmethod
    def update_email(self, email: str):
        pass
