from abc import ABC, abstractmethod
from fastapi import File, UploadFile


class DetectService(ABC):

    @abstractmethod
    def detect_video(self, user_id: int, username: str, file: UploadFile = File(...)):
        pass

    @abstractmethod
    async def ig_reel(self, user_id: int, username: str, url: str):
        pass

    @abstractmethod
    async def twitter_video(self, user_id: int, username: str, url: str):
        pass

    @abstractmethod
    async def youtube_video(self, user_id: int, username: str, url: str):
        pass

    @abstractmethod
    async def facebook(self, user_id: int, username: str, url: str):
        pass
