from sqlalchemy.orm import Session, aliased
from models.Prediction import Prediction
from operator import and_

from models.Video import Video


class PredictionDAO:
    def __init__(self, db: Session):
        self.db = db

    def get_all_predictions(self):
        videoalias = aliased(Video)
        return (
            self.db.query(
                Prediction.pred_id,
                Prediction.user_id,
                Prediction.pred_label,
                videoalias.filename,
                videoalias.source,
                videoalias.url
            )
            .join(videoalias, videoalias.video_id == Prediction.video_id)
            .all()
        )

    def get_prediction_by_id(self, pred_id: int):
        videoalias = aliased(Video)
        return (
            self.db.query(
                Prediction.pred_id,
                Prediction.user_id,
                Prediction.pred_label,
                videoalias.filename,
                videoalias.source,
                videoalias.url
            )
            .join(videoalias, videoalias.video_id == Prediction.video_id)
            .filter(Prediction.pred_id == pred_id)
            .first()
        )

    def get_predictions_by_userid(self, user_id: int):
        videoalias = aliased(Video)
        return (
            self.db.query(
                Prediction.pred_id,
                Prediction.user_id,
                Prediction.pred_label,
                videoalias.filename,
                videoalias.source,
                videoalias.url
            )
            .join(videoalias, videoalias.video_id == Prediction.video_id)
            .filter(Prediction.user_id == user_id)
            .filter(videoalias.user_id == user_id)
            .all()
        )

    def get_predictions_by_videoid(self, video_id: int):
        videoalias = aliased(Video)
        return (
            self.db.query(
                Prediction.pred_id,
                Prediction.user_id,
                Prediction.pred_label,
                videoalias.filename,
                videoalias.source,
                videoalias.url
            )
            .join(videoalias, videoalias.video_id == Prediction.video_id)
            .filter(Prediction.video_id == video_id)
            .all()
        )

    def get_prediction_by_multiple_filters(self, filters: list):
        videoalias = aliased(Video)
        return (
            self.db.query(
                Prediction.pred_id,
                Prediction.user_id,
                Prediction.pred_label,
                videoalias.filename,
                videoalias.source,
                videoalias.url
            )
            .join(videoalias, videoalias.video_id == Prediction.video_id)
            .filter(and_(*filters))
            .all()
        )

    def create_prediction(self, prediction: Prediction):
        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)
        return prediction

    def delete_prediction(self, pred_id: int):
        prediction: Prediction = self.db.query(Prediction).filter(Prediction.pred_id == pred_id).first()
        self.db.delete(prediction)
        self.db.commit()
