from abc import ABC, abstractmethod
from dto.req.AuthReqDto import AuthReqDto


class AuthService(ABC):

    @abstractmethod
    def login(self, creds: AuthReqDto):
        pass

    @abstractmethod
    def logout(self, token: str, user_id: int):
        pass
