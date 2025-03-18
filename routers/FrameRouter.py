from fastapi import APIRouter, Query
from typing import Optional, List

from starlette.responses import JSONResponse

from dto.req.FrameReqDto import FrameReqDto
from dto.res.ErrorResDto import ErrorResDto
from dto.res.UnauthenticatedResDto import UnauthenticatedResDto
from models.Frame import Frame
from config.database import db_dependency
from services.impl.FrameServiceImpl import FrameServiceImpl
from dto.res.GeneralMsgResDto import GeneralMsgResDto
from dto.res.FrameResDto import FrameResDto
from routers.AuthRouter import user_dependency

router = APIRouter(prefix="/api/v1/frames", tags=["Frames"])


@router.get("",
            response_model=List[FrameResDto] | FrameResDto,
            responses={
                401: {"model": UnauthenticatedResDto, "description": "Unauthorised"},
                404: {"model": GeneralMsgResDto, "description": "Frame not found"},
                400: {"model": GeneralMsgResDto, "description": "Bad Request"},
                500: {"model": GeneralMsgResDto, "description": "Internal Server Error"}
            }
            )
async def get_frames(
        user: user_dependency,
        db: db_dependency,
        frame_id: Optional[int] = Query(None, description="Enter the frame ID to find frame with frame_id"),
        user_id: Optional[int] = Query(None, description="Enter the user ID to find frame with user_id"),
        video_id: Optional[int] = Query(None, description="Enter the video ID to find frame with video_id")
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

    frame_service = FrameServiceImpl(db)

    if user_id and not frame_id and not video_id:
        return frame_service.get_frame_by_user_id(user_id)

    elif frame_id and not user_id and not video_id:
        return frame_service.get_frame_by_frame_id(frame_id)

    elif video_id and not frame_id and not user_id:
        return frame_service.get_frame_by_video_id(video_id)

    filters = []
    if frame_id:
        filters.append(Frame.frame_id == frame_id)
    if user_id:
        filters.append(Frame.user_id == user_id)
    if video_id:
        filters.append(Frame.video_id == video_id)

    if filters:
        return frame_service.get_frame_by_multiple_filters(filters)

    return frame_service.get_frames()


@router.post("",
             response_model=GeneralMsgResDto,
             responses={
                 401: {"model": UnauthenticatedResDto, "description": "Unauthorised"},
                 404: {"model": GeneralMsgResDto, "description": "Frame not found"},
                 400: {"model": GeneralMsgResDto, "description": "Bad Request"},
                 500: {"model": GeneralMsgResDto, "description": "Internal Server Error"}
             }
             )
async def post_frame(
        user: user_dependency,
        db: db_dependency,
        frame: FrameReqDto,
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
    if not frame:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message="Please enter all details",
                details=f"Please enter frame details.",
            ),
            message="Request could not be completed due to an error.",
        )
        return JSONResponse(content=error_res.dict(), status_code=400)
    elif not frame.filename:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message="Please enter filename of frame.",
                details=f"Please enter filename of a frame.",
            ),
            message="Request could not be completed due to an error.",
        )
        return JSONResponse(content=error_res.dict(), status_code=400)

    frame_service = FrameServiceImpl(db)
    return frame_service.add_frame(frame, user["user_id"])


@router.delete("",
               response_model=GeneralMsgResDto,
               responses={
                   401: {"model": UnauthenticatedResDto, "description": "Unauthorised"},
                   404: {"model": GeneralMsgResDto, "description": "Frame not found"},
                   400: {"model": GeneralMsgResDto, "description": "Bad Request"},
                   500: {"model": GeneralMsgResDto, "description": "Internal Server Error"}
               }
               )
async def delete_frame(
        user: user_dependency,
        db: db_dependency,
        frame_id: int = Query(description="Enter the frame id to delete frame")
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

    if not frame_id:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message="Please enter frame id",
                details=f"Please enter frame id to delete a frame.",
            ),
            message="Request could not be completed due to an error.",
        )
        return JSONResponse(content=error_res.dict(), status_code=400)

    frame_service = FrameServiceImpl(db)
    return frame_service.delete_frame(frame_id)
