from abc import ABC, abstractmethod
from fastapi import File, UploadFile


class DetectService(ABC):

    @abstractmethod
    def detect_video(self, user_id: int, username: str, file: UploadFile = File(...)):
        pass
