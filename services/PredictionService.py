from abc import ABC, abstractmethod


class PredictionService(ABC):

    @abstractmethod
    def get_predictions(self):
        pass

    @abstractmethod
    def get_prediction_by_prediction_id(self, pred_id: int):
        pass

    @abstractmethod
    def get_prediction_by_user_id(self, user_id: int):
        pass

    @abstractmethod
    def get_prediction_by_video_id(self, video_id: int):
        pass

    @abstractmethod
    def get_prediction_by_multiple_filters(self, filters: list):
        pass

    @abstractmethod
    def add_prediction(self, user_id: int, video_id: int, pred_label: str):
        pass

    @abstractmethod
    def delete_prediction(self, pred_id: int):
        pass
