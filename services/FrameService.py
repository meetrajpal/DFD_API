from abc import ABC, abstractmethod

from dto.req.FrameReqDto import FrameReqDto


class FrameService(ABC):

    @abstractmethod
    def get_frames(self):
        pass

    @abstractmethod
    def get_frame_by_frame_id(self, frame_id: int):
        pass

    @abstractmethod
    def get_frame_by_user_id(self, user_id: int):
        pass

    @abstractmethod
    def get_frame_by_video_id(self, video_id: int):
        pass

    @abstractmethod
    def get_frame_by_multiple_filters(self, filters: list):
        pass

    @abstractmethod
    def add_frame(self, frame: FrameReqDto, user_id: int):
        pass

    @abstractmethod
    def delete_frame(self, frame_id: int):
        pass
