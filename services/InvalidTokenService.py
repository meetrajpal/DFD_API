from abc import ABC, abstractmethod


class InvalidTokenService(ABC):

    @abstractmethod
    def get_by_token(self, token: str):
        pass

    @abstractmethod
    def expire_token(self, token: str):
        pass
