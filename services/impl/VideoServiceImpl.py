import traceback

from dao.VideoDAO import VideoDAO
from sqlalchemy.orm import Session

from fastapi.responses import JSONResponse

from dto.req.VideoReqDto import VideoReqDto
from dto.res.ErrorResDto import ErrorResDto
from dto.res.GeneralMsgResDto import GeneralMsgResDto
from models.Video import Video
from services.VideoService import VideoService
from services.impl.UserServiceImpl import UserServiceImpl


class VideoServiceImpl(VideoService):

    def __init__(self, db: Session):
        self.db = db
        self.dao = VideoDAO(db)

    def get_videos(self):
        return self.dao.get_all_videos()

    def get_video_by_video_id(self, video_id: int):
        video = self.dao.get_video_by_id(video_id)
        if video is None:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="not_found",
                    message="Video not found",
                    details=f"Video not found with video_id: {video_id}",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=404)
        return video

    def get_video_by_user_id(self, user_id: int):
        user_service = UserServiceImpl(self.db)
        user_service.get_user_by_id(user_id)
        videos = self.dao.get_videos_by_userid(user_id)
        if len(videos) == 0:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="not_found",
                    message="Video not found",
                    details=f"Video not found with user_id: {user_id}",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=404)
        return videos

    def get_video_by_multiple_filters(self, filters: list):
        videos = self.dao.get_video_by_multiple_filters(filters)
        if len(videos) == 0:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="not_found",
                    message="Video not found",
                    details=f"Video not found with given filters.",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=404)
        return videos

    def add_video(self, filename: str, file_path: str, user_id: int):
        data: Video = self.dao.get_videos_by_userid_filename(user_id, filename)
        if data and data.filename == filename:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="bad_request",
                    message="A video with same filename already exists.",
                    details=f"A video with same filename already exists.",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=400)
        try:
            new_video = self.dao.create_video(Video(user_id, filename, file_path))
        except Exception as e:
            # print(traceback.print_exc())
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="internal_server_error",
                    message="Error occurred while creating video record.",
                    details=f"Error occurred while creating video record: {e}",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=500)

        return new_video

    def delete_video(self, video_id: int):
        video = self.dao.get_video_by_id(video_id)
        if not video:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="not_found",
                    message="Video not found",
                    details=f"Video not found with video_id: {video_id}",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=404)

        try:
            self.dao.delete_video(video)
        except Exception as e:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="internal_server_error",
                    message="Error occurred while deleting video.",
                    details=f"Error occurred while deleting video: {e}",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=500)

        success = GeneralMsgResDto(
            isSuccess=True,
            hasException=False,
            message="Video deleted successfully.",
        )
        return JSONResponse(content=success.dict(), status_code=200)
