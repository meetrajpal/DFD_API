from typing import Optional, List

from fastapi import APIRouter, Query
from starlette.responses import JSONResponse

from config.database import db_dependency
from dto.res.ErrorResDto import ErrorResDto
from dto.res.GeneralMsgResDto import GeneralMsgResDto
from dto.res.UnauthenticatedResDto import UnauthenticatedResDto
from dto.res.UserResDto import UserResDto
from models.User import User
from services.impl.UserServiceImpl import UserServiceImpl
from routers.AuthRouter import user_dependency

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get("",
            response_model=List[UserResDto] | UserResDto,
            responses={
                401: {"model": UnauthenticatedResDto, "description": "Unauthorised"},
                404: {"model": GeneralMsgResDto, "description": "User not found"},
                400: {"model": GeneralMsgResDto, "description": "Bad Request"},
                500: {"model": GeneralMsgResDto, "description": "Internal Server Error"}
            }
            )
async def get_users(
        db: db_dependency,
        user: user_dependency,
        username: Optional[str] = Query(None, description="Enter the username to find user with username"),
        email: Optional[str] = Query(None, description="Enter the email to find user with email"),
        user_id: Optional[int] = Query(None, description="Enter the user ID to find user with user_id")
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

    user_service = UserServiceImpl(db)

    if username and not email and not user_id:
        return user_service.get_user_by_username(username)

    elif email and not username and not user_id:
        return user_service.get_user_by_email(email)

    elif user_id and not username and not email:
        return user_service.get_user_by_id(user_id)

    filters = []
    if username:
        filters.append(User.username == username)
    if email:
        filters.append(User.email == email)
    if user_id:
        filters.append(User.user_id == user_id)

    if filters:
        return user_service.get_user_by_multiple_filters(filters)

    return user_service.get_users()


@router.delete("",
               response_model=GeneralMsgResDto,
               responses={
                   401: {"model": UnauthenticatedResDto, "description": "Unauthorised"},
                   404: {"model": GeneralMsgResDto, "description": "User not found"},
                   400: {"model": GeneralMsgResDto, "description": "Bad Request"},
                   500: {"model": GeneralMsgResDto, "description": "Internal Server Error"}
               }
               )
async def delete_user(
        user: user_dependency,
        db: db_dependency,
        user_id: int = Query(description="Enter the user id to delete user")
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

    if not user_id:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message="Please enter user id",
                details=f"Please enter user id to delete a user.",
            ),
            message="Request could not be completed due to an error.",
        )
        return JSONResponse(content=error_res.dict(), status_code=400)

    user_service = UserServiceImpl(db)
    return user_service.delete_user(user_id)
