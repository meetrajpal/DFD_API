import os
from config.database import db_dependency
from fastapi.responses import JSONResponse
from dto.res.ErrorResDto import ErrorResDto
from routers.AuthRouter import user_dependency
from fastapi import APIRouter, File, UploadFile, Query
from dto.res.GeneralMsgResDto import GeneralMsgResDto
from services.impl.DetectServiceImpl import DetectServiceImpl
from dto.res.UnauthenticatedResDto import UnauthenticatedResDto

router = APIRouter(prefix="/api/v1/detect", tags=["Detect Deepfake"])

os.makedirs(os.getenv("UPLOAD_DIR"), exist_ok=True)


@router.post("/direct-upload",
             response_model=GeneralMsgResDto,
             responses={
                 401: {"model": UnauthenticatedResDto, "description": "Unauthorised"},
                 404: {"model": GeneralMsgResDto, "description": "Not found"},
                 400: {"model": GeneralMsgResDto, "description": "Bad Request"},
                 500: {"model": GeneralMsgResDto, "description": "Internal Server Error"}
             }
             )
async def upload_video(
        user: user_dependency,
        db: db_dependency,
        file: UploadFile = File(...)
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

    allowed_extensions = {"mp4", "avi", "mov", "mkv"}
    file_extension = file.filename.split(".")[-1].lower()

    if file_extension not in allowed_extensions:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message=f"Invalid file format: {file_extension}",
                details=f"Only {allowed_extensions} are allowed",
            ),
            message="Request could not be completed due to an error."
        )
        return JSONResponse(content=error_res.dict(), status_code=400)

    detect_service = DetectServiceImpl(db)
    return detect_service.detect_video(user["user_id"], user["username"], file)


@router.get("/ig-reel",
            response_model=GeneralMsgResDto,
            responses={
                401: {"model": UnauthenticatedResDto, "description": "Unauthorised"},
                404: {"model": GeneralMsgResDto, "description": "Not found"},
                400: {"model": GeneralMsgResDto, "description": "Bad Request"},
                500: {"model": GeneralMsgResDto, "description": "Internal Server Error"}
            }
            )
async def insta_reel(
        user: user_dependency,
        db: db_dependency,
        url: str = Query(description="Enter valid url of instagram reel")
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

    if not url:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message="Please enter url of instagram reel",
                details=f"Url cannot be empty"
            ),
            message="Request could not be completed due to an error."
        )
        return JSONResponse(content=error_res.dict(), status_code=400)

    if ("https://www.instagram.com/reels" not in url) & ("https://www.instagram.com/p" not in url):
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message="Please enter valid url of instagram reel",
                details="This URL not seems to be valid for instagram reel. Make sure it looks like https://www.instagram.com/p/B61OVIsgx_6/?igsh=NTc4MTIwNjQ2YQ=="
            ),
            message="Request could not be completed due to an error."
        )
        return JSONResponse(content=error_res.dict(), status_code=400)

    detect_service = DetectServiceImpl(db)
    return await detect_service.ig_reel(user["user_id"], user["username"], url)


@router.get("/twitter-video",
            response_model=GeneralMsgResDto,
            responses={
                401: {"model": UnauthenticatedResDto, "description": "Unauthorised"},
                404: {"model": GeneralMsgResDto, "description": "Not found"},
                400: {"model": GeneralMsgResDto, "description": "Bad Request"},
                500: {"model": GeneralMsgResDto, "description": "Internal Server Error"}
            }
            )
async def twitter_video(
        user: user_dependency,
        db: db_dependency,
        url: str = Query(description="Enter valid url of twitter video/status")
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

    if not url:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message="Please enter url of twitter status or video",
                details=f"Url cannot be empty"
            ),
            message="Request could not be completed due to an error."
        )
        return JSONResponse(content=error_res.dict(), status_code=400)

    if "https://x.com" not in url:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message="Please enter valid url of twitter video.",
                details="This URL not seems to be valid for twitter video. Make sure it looks like https://x.com/TedCruz1072676/status/1905223889875288355"
            ),
            message="Request could not be completed due to an error."
        )
        return JSONResponse(content=error_res.dict(), status_code=400)

    detect_service = DetectServiceImpl(db)
    return await detect_service.twitter_video(user["user_id"], user["username"], url)


@router.get("/youtube-video",
            response_model=GeneralMsgResDto,
            responses={
                401: {"model": UnauthenticatedResDto, "description": "Unauthorised"},
                404: {"model": GeneralMsgResDto, "description": "Not found"},
                400: {"model": GeneralMsgResDto, "description": "Bad Request"},
                500: {"model": GeneralMsgResDto, "description": "Internal Server Error"}
            }
            )
async def youtube_video(
        user: user_dependency,
        db: db_dependency,
        url: str = Query(description="Enter valid url of youtube video")
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

    if not url:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message="Please enter url of youtube video",
                details=f"Url cannot be empty"
            ),
            message="Request could not be completed due to an error."
        )
        return JSONResponse(content=error_res.dict(), status_code=400)

    if "https://youtu.be" not in url:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message="Please enter valid url of youtube video",
                details="This URL not seems to be valid for youtube video. Make sure it looks like https://youtu.be/uEg9_M4YaJk?si=mxrCu2F8btZKhQt7"
            ),
            message="Request could not be completed due to an error."
        )
        return JSONResponse(content=error_res.dict(), status_code=400)

    detect_service = DetectServiceImpl(db)
    return await detect_service.youtube_video(user["user_id"], user["username"], url)


@router.get("/facebook",
            response_model=GeneralMsgResDto,
            responses={
                401: {"model": UnauthenticatedResDto, "description": "Unauthorised"},
                404: {"model": GeneralMsgResDto, "description": "Not found"},
                400: {"model": GeneralMsgResDto, "description": "Bad Request"},
                500: {"model": GeneralMsgResDto, "description": "Internal Server Error"}
            }
            )
async def facebook(
        user: user_dependency,
        db: db_dependency,
        url: str = Query(description="Enter valid url of youtube video")
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

    if not url:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message="Please enter url of facebook reel or video",
                details=f"Url cannot be empty"
            ),
            message="Request could not be completed due to an error."
        )
        return JSONResponse(content=error_res.dict(), status_code=400)

    if "https://www.facebook.com/share" not in url:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message="Please enter valid url of facebook",
                details="This URL not seems to be valid for facebook video. Make sure it is like https://www.facebook.com/share/v/1ETMqmyaqw/"
            ),
            message="Request could not be completed due to an error."
        )
        return JSONResponse(content=error_res.dict(), status_code=400)

    detect_service = DetectServiceImpl(db)
    return await detect_service.facebook(user["user_id"], user["username"], url)
