import re
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from config.database import db_dependency
from dto.req.ForgotPasswordMailClickReqDto import ForgotPasswordMailClickReqDto
from dto.req.UpdateEmailMailClickReqDto import UpdateEmailMailClickReqDto
from dto.res.ErrorResDto import ErrorResDto
from dto.res.GeneralMsgResDto import GeneralMsgResDto
from services.impl.InvalidTokenServiceImpl import InvalidTokenServiceImpl
from services.impl.UserServiceImpl import UserServiceImpl

router = APIRouter(prefix="/api/v1/mail", tags=["Mail Link Click API"])


@router.get("/verify-email/{token}",
            response_model=GeneralMsgResDto,
            responses={
                404: {"model": GeneralMsgResDto, "description": "User not found"},
                400: {"model": GeneralMsgResDto, "description": "Bad Request"},
                500: {"model": GeneralMsgResDto, "description": "Internal Server Error"}
            }
            )
async def verify_email(
        db: db_dependency,
        token: str
):
    if not token:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message="Token is missing.",
                details=f"Token not found in the url.",
            ),
            message="Request could not be completed due to an error.",
        )
        return JSONResponse(content=error_res.dict(), status_code=400)

    invalid_token_service = InvalidTokenServiceImpl(db)
    if invalid_token_service.get_by_token(token) is not None:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message="Token is expired.",
                details=f"Token is expired which is given in the url."
            ),
            message="Request could not be completed due to an error.",
        )
        return JSONResponse(content=error_res.dict(), status_code=400)

    user_service = UserServiceImpl(db)
    return user_service.verify_email(token)


@router.put("/forgot-password/{token}",
            response_model=GeneralMsgResDto,
            responses={
                404: {"model": GeneralMsgResDto, "description": "User not found"},
                400: {"model": GeneralMsgResDto, "description": "Bad Request"},
                500: {"model": GeneralMsgResDto, "description": "Internal Server Error"}
            }
            )
async def forgot_password(
        db: db_dependency,
        token: str,
        user: ForgotPasswordMailClickReqDto
):
    if not token:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message="Token is missing.",
                details=f"Token not found in the url.",
            ),
            message="Request could not be completed due to an error.",
        )
        return JSONResponse(content=error_res.dict(), status_code=400)
    elif not user or not user.password:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message="Please fill password",
                details=f"You can not leave password empty",
            ),
            message="Request could not be completed due to an error.",
        )
        return JSONResponse(content=error_res.dict(), status_code=400)
    elif not user or not user.cnf_password:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message="Please fill confirm password",
                details=f"You can not leave confirm password empty",
            ),
            message="Request could not be completed due to an error.",
        )
        return JSONResponse(content=error_res.dict(), status_code=400)
    elif user.password != user.cnf_password:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message="Passwords do not match",
                details=f"Both Passwords do not match",
            ),
            message="Request could not be completed due to an error.",
        )
        return JSONResponse(content=error_res.dict(), status_code=400)

    invalid_token_service = InvalidTokenServiceImpl(db)
    if invalid_token_service.get_by_token(token) is not None:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message="Token is expired.",
                details=f"Token is expired which is given in the url."
            ),
            message="Request could not be completed due to an error.",
        )
        return JSONResponse(content=error_res.dict(), status_code=400)

    user_service = UserServiceImpl(db)
    return user_service.reset_password(token, user.cnf_password)


@router.put("/update-email/{token}",
            response_model=GeneralMsgResDto,
            responses={
                404: {"model": GeneralMsgResDto, "description": "User not found"},
                400: {"model": GeneralMsgResDto, "description": "Bad Request"},
                500: {"model": GeneralMsgResDto, "description": "Internal Server Error"}
            }
            )
async def update_email(
        db: db_dependency,
        token: str,
        user: UpdateEmailMailClickReqDto
):
    if not token:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message="Token is missing.",
                details=f"Token not found in the url.",
            ),
            message="Request could not be completed due to an error.",
        )
        return JSONResponse(content=error_res.dict(), status_code=400)
    elif not user or not user.email:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message="Please fill email field",
                details=f"You can not leave email field empty",
            ),
            message="Request could not be completed due to an error.",
        )
        return JSONResponse(content=error_res.dict(), status_code=400)
    elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', user.email):
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message="Please enter a valid email address",
                details=f"Invalid email address: {user.email}",
            ),
            message="Request could not be completed due to an error.",
        )
        return JSONResponse(content=error_res.dict(), status_code=400)

    invalid_token_service = InvalidTokenServiceImpl(db)
    if invalid_token_service.get_by_token(token) is not None:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message="Token is expired.",
                details=f"Token is expired which is given in the url."
            ),
            message="Request could not be completed due to an error.",
        )
        return JSONResponse(content=error_res.dict(), status_code=400)

    user_service = UserServiceImpl(db)
    return user_service.update_email(token, user.email)
