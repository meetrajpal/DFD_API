import traceback

from dao.PredictionDAO import PredictionDAO
from sqlalchemy.orm import Session

from fastapi.responses import JSONResponse

from dto.res.ErrorResDto import ErrorResDto
from dto.res.GeneralMsgResDto import GeneralMsgResDto
from models.Prediction import Prediction
from services.PredictionService import PredictionService
from services.impl.UserServiceImpl import UserServiceImpl
from services.impl.VideoServiceImpl import VideoServiceImpl


class PredictionServiceImpl(PredictionService):

    def __init__(self, db: Session):
        self.db = db
        self.dao = PredictionDAO(db)

    def get_predictions(self):
        return self.dao.get_all_predictions()

    def get_prediction_by_prediction_id(self, pred_id: int):
        prediction = self.dao.get_prediction_by_id(pred_id)
        if prediction is None:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="not_found",
                    message="Prediction not found",
                    details=f"Prediction not found with prediction_id: {pred_id}",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=404)
        return prediction

    def get_prediction_by_user_id(self, user_id: int):
        user_service = UserServiceImpl(self.db)
        user_service.get_user_by_id(user_id)
        predictions = self.dao.get_predictions_by_userid(user_id)
        if len(predictions) == 0:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="not_found",
                    message="Prediction not found",
                    details=f"Prediction not found with user_id: {user_id}",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=404)
        return predictions

    def get_prediction_by_video_id(self, video_id: int):
        video_service = VideoServiceImpl(self.db)
        video_service.get_video_by_video_id(video_id)
        predictions = self.dao.get_predictions_by_videoid(video_id)
        if len(predictions) == 0:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="not_found",
                    message="Prediction not found",
                    details=f"Prediction not found with video_id: {video_id}",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=404)
        return predictions

    def get_prediction_by_multiple_filters(self, filters: list):
        predictions = self.dao.get_prediction_by_multiple_filters(filters)
        if len(predictions) == 0:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="not_found",
                    message="Prediction not found",
                    details=f"Prediction not found with given filters.",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=404)
        return predictions

    def add_prediction(self, user_id: int, video_id: int, pred_label: str):
        try:
            new_prediction = self.dao.create_prediction(Prediction(user_id, video_id, pred_label))
        except Exception as e:
            # print(traceback.print_exc())
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="internal_server_error",
                    message="Error occurred while creating prediction record.",
                    details=f"Error occurred while creating prediction record: {e}",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=500)

        return new_prediction

    def delete_prediction(self, pred_id: int):
        prediction = self.dao.get_prediction_by_id(pred_id)
        if not prediction:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="not_found",
                    message="Prediction not found",
                    details=f"Prediction not found with prediction_id: {pred_id}",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=404)

        try:
            self.dao.delete_prediction(prediction)
        except Exception as e:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="internal_server_error",
                    message="Error occurred while deleting prediction.",
                    details=f"Error occurred while deleting prediction: {e}",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=500)

        success = GeneralMsgResDto(
            isSuccess=True,
            hasException=False,
            message="Prediction deleted successfully.",
        )
        return JSONResponse(content=success.dict(), status_code=200)
