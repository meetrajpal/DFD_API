from fastapi import APIRouter, Query
from typing import Optional, List

from starlette.responses import JSONResponse

from dto.req.VideoReqDto import VideoReqDto
from dto.res.ErrorResDto import ErrorResDto
from dto.res.UnauthenticatedResDto import UnauthenticatedResDto
from models.Video import Video
from config.database import db_dependency
from services.impl.VideoServiceImpl import VideoServiceImpl
from dto.res.GeneralMsgResDto import GeneralMsgResDto
from dto.res.VideoResDto import VideoResDto
from routers.AuthRouter import user_dependency

router = APIRouter(prefix="/api/v1/videos", tags=["Videos"])


@router.get("",
            response_model=List[VideoResDto] | VideoResDto,
            responses={
                401: {"model": UnauthenticatedResDto, "description": "Unauthorised"},
                404: {"model": GeneralMsgResDto, "description": "Video not found"},
                400: {"model": GeneralMsgResDto, "description": "Bad Request"},
                500: {"model": GeneralMsgResDto, "description": "Internal Server Error"}
            }
            )
async def get_videos(
        user: user_dependency,
        db: db_dependency,
        video_id: Optional[int] = Query(None, description="Enter the video ID to find video with video_id"),
        user_id: Optional[int] = Query(None, description="Enter the user ID to find video with user_id")
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

    video_service = VideoServiceImpl(db)

    if user_id and not video_id:
        return video_service.get_video_by_user_id(user_id)

    elif video_id and not user_id:
        return video_service.get_video_by_video_id(video_id)

    filters = []
    if video_id:
        filters.append(Video.video_id == video_id)
    if user_id:
        filters.append(Video.user_id == user_id)

    if filters:
        return video_service.get_video_by_multiple_filters(filters)

    return video_service.get_videos()


@router.post("",
             response_model=GeneralMsgResDto,
             responses={
                 401: {"model": UnauthenticatedResDto, "description": "Unauthorised"},
                 404: {"model": GeneralMsgResDto, "description": "Video not found"},
                 400: {"model": GeneralMsgResDto, "description": "Bad Request"},
                 500: {"model": GeneralMsgResDto, "description": "Internal Server Error"}
             }
             )
async def post_video(
        user: user_dependency,
        db: db_dependency,
        video: VideoReqDto,
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
    if not video:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message="Please enter all details",
                details=f"Please enter video details.",
            ),
            message="Request could not be completed due to an error.",
        )
        return JSONResponse(content=error_res.dict(), status_code=400)
    elif not video.filename:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message="Please enter filename of video.",
                details=f"Please enter filename of a video.",
            ),
            message="Request could not be completed due to an error.",
        )
        return JSONResponse(content=error_res.dict(), status_code=400)

    video_service = VideoServiceImpl(db)
    return video_service.add_video(video.filename, video.filepath, user["user_id"])


@router.delete("",
               response_model=GeneralMsgResDto,
               responses={
                   401: {"model": UnauthenticatedResDto, "description": "Unauthorised"},
                   404: {"model": GeneralMsgResDto, "description": "Video not found"},
                   400: {"model": GeneralMsgResDto, "description": "Bad Request"},
                   500: {"model": GeneralMsgResDto, "description": "Internal Server Error"}
               }
               )
async def delete_video(
        user: user_dependency,
        db: db_dependency,
        video_id: int = Query(description="Enter the video id to delete video")
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

    if not video_id:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message="Please enter video id",
                details=f"Please enter video id to delete a video.",
            ),
            message="Request could not be completed due to an error.",
        )
        return JSONResponse(content=error_res.dict(), status_code=400)

    video_service = VideoServiceImpl(db)
    return video_service.delete_video(video_id)
