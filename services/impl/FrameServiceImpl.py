from models.Frame import Frame
from dao.FrameDAO import FrameDAO
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from dto.req.FrameReqDto import FrameReqDto
from dto.res.ErrorResDto import ErrorResDto
from services.FrameService import FrameService
from dto.res.GeneralMsgResDto import GeneralMsgResDto
from services.impl.UserServiceImpl import UserServiceImpl


class FrameServiceImpl(FrameService):

    def __init__(self, db: Session):
        self.db = db
        self.dao = FrameDAO(db)

    def get_frames(self):
        return self.dao.get_all_frames()

    def get_frame_by_frame_id(self, frame_id: int):
        frame = self.dao.get_frame_by_id(frame_id)
        if frame is None:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="not_found",
                    message="Frame not found",
                    details=f"Frame not found with frame_id: {frame_id}",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=404)
        return frame

    def get_frame_by_video_id(self, video_id: int):
        frame = self.dao.get_frame_by_videoid(video_id)
        if frame is None:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="not_found",
                    message="Frame not found",
                    details=f"Frame not found with video_id: {video_id}",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=404)
        return frame

    def get_frame_by_user_id(self, user_id: int):
        user_service = UserServiceImpl(self.db)
        user_service.get_user_by_id(user_id)
        frames = self.dao.get_frames_by_userid(user_id)
        if len(frames) == 0:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="not_found",
                    message="Frame not found",
                    details=f"Frame not found with user_id: {user_id}",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=404)
        return frames

    def get_frame_by_multiple_filters(self, filters: list):
        frames = self.dao.get_frame_by_multiple_filters(filters)
        if len(frames) == 0:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="not_found",
                    message="Frame not found",
                    details=f"Frame not found with given filters.",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=404)
        return frames

    def add_frame(self, frame: FrameReqDto, user_id: int):
        data: Frame = self.dao.get_frames_by_videoid_userid_filename(frame.video_id, user_id, frame.filename)
        if data is not None and data.filename == frame.filename:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="bad_request",
                    message="A frame with same filename already exists.",
                    details=f"A frame with same filename already exists.",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=400)
        try:
            self.dao.create_frame(Frame(frame.video_id, user_id, frame.filename, frame.filepath))
        except Exception as e:
            # print(traceback.print_exc())
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="internal_server_error",
                    message="Error occurred while creating frame record.",
                    details=f"Error occurred while creating frame record: {e}",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=500)

        success = GeneralMsgResDto(
            isSuccess=True,
            hasException=False,
            message="Frame record successfully created.",
        )
        return JSONResponse(content=success.dict(), status_code=200)

    def delete_frame(self, frame_id: int):
        frame = self.dao.get_frame_by_id(frame_id)
        if not frame:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="not_found",
                    message="Frame not found",
                    details=f"Frame not found with frame_id: {frame_id}",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=404)

        try:
            self.dao.delete_frame(frame)
        except Exception as e:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="internal_server_error",
                    message="Error occurred while deleting frame.",
                    details=f"Error occurred while deleting frame: {e}",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=500)

        success = GeneralMsgResDto(
            isSuccess=True,
            hasException=False,
            message="Frame deleted successfully.",
        )
        return JSONResponse(content=success.dict(), status_code=200)
