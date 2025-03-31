from abc import ABC, abstractmethod


class VideoService(ABC):

    @abstractmethod
    def get_videos(self):
        pass

    @abstractmethod
    def get_video_by_video_id(self, video_id: int):
        pass

    @abstractmethod
    def get_video_by_user_id(self, user_id: int):
        pass

    @abstractmethod
    def get_video_by_multiple_filters(self, filters: list):
        pass

    @abstractmethod
    def add_video(self, filename: str, file_path: str, user_id: int, source: str, url: str):
        pass

    @abstractmethod
    def delete_video(self, video_id: int):
        pass
