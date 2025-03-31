from models.Video import Video
from typing import Optional, List
from fastapi import APIRouter, Query
from config.database import db_dependency
from dto.res.VideoResDto import VideoResDto
from dto.res.ErrorResDto import ErrorResDto
from starlette.responses import JSONResponse
from routers.AuthRouter import user_dependency
from dto.res.GeneralMsgResDto import GeneralMsgResDto
from services.impl.VideoServiceImpl import VideoServiceImpl
from dto.res.UnauthenticatedResDto import UnauthenticatedResDto

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
