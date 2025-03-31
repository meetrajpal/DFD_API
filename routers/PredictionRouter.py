from models.Prediction import Prediction
from typing import Optional, List
from fastapi import APIRouter, Query
from config.database import db_dependency
from dto.res.PredictionResDto import PredictionResDto
from dto.res.ErrorResDto import ErrorResDto
from starlette.responses import JSONResponse
from routers.AuthRouter import user_dependency
from dto.res.GeneralMsgResDto import GeneralMsgResDto
from services.impl.PredictionServiceImpl import PredictionServiceImpl
from dto.res.UnauthenticatedResDto import UnauthenticatedResDto

router = APIRouter(prefix="/api/v1/predictions", tags=["Predictions"])


@router.get("",
            response_model=List[PredictionResDto] | PredictionResDto,
            responses={
                401: {"model": UnauthenticatedResDto, "description": "Unauthorised"},
                404: {"model": GeneralMsgResDto, "description": "Prediction not found"},
                400: {"model": GeneralMsgResDto, "description": "Bad Request"},
                500: {"model": GeneralMsgResDto, "description": "Internal Server Error"}
            }
            )
async def get_predictions(
        user: user_dependency,
        db: db_dependency,
        pred_id: Optional[int] = Query(None, description="Enter the prediction ID to find prediction with prediction_id"),
        user_id: Optional[int] = Query(None, description="Enter the user ID to find prediction with user_id"),
        video_id: Optional[int] = Query(None, description="Enter the video ID to find prediction with video_id")
):
    if user is None:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="unauthorized",
                message="Authentication failed, please log in to access this resource.",
                details=f"Full authentication is required to access this resource.",
            ),
            message="Request could not be completed due to an error.",
        )
        return JSONResponse(content=error_res.dict(), status_code=401)

    prediction_service = PredictionServiceImpl(db)

    if user_id and not pred_id and not video_id:
        return prediction_service.get_prediction_by_user_id(user_id)

    elif pred_id and not user_id and not video_id:
        return prediction_service.get_prediction_by_prediction_id(pred_id)

    elif video_id and not user_id and not pred_id:
        return prediction_service.get_prediction_by_video_id(video_id)

    filters = []
    if pred_id:
        filters.append(Prediction.pred_id == pred_id)
    if user_id:
        filters.append(Prediction.user_id == user_id)
    if video_id:
        filters.append(Prediction.video_id == video_id)

    if filters:
        return prediction_service.get_prediction_by_multiple_filters(filters)

    return prediction_service.get_predictions()


@router.delete("",
               response_model=GeneralMsgResDto,
               responses={
                   401: {"model": UnauthenticatedResDto, "description": "Unauthorised"},
                   404: {"model": GeneralMsgResDto, "description": "Prediction not found"},
                   400: {"model": GeneralMsgResDto, "description": "Bad Request"},
                   500: {"model": GeneralMsgResDto, "description": "Internal Server Error"}
               }
               )
async def delete_prediction(
        user: user_dependency,
        db: db_dependency,
        prediction_id: int = Query(description="Enter the prediction id to delete prediction")
):
    if user is None:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="unauthorized",
                message="Authentication failed, please log in to access this resource.",
                details=f"Full authentication is required to access this resource.",
            ),
            message="Request could not be completed due to an error.",
        )
        return JSONResponse(content=error_res.dict(), status_code=401)

    if not prediction_id:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message="Please enter prediction id",
                details=f"Please enter prediction id to delete a prediction.",
            ),
            message="Request could not be completed due to an error.",
        )
        return JSONResponse(content=error_res.dict(), status_code=400)

    prediction_service = PredictionServiceImpl(db)
    return prediction_service.delete_prediction(prediction_id)
