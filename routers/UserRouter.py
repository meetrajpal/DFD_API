from fastapi import APIRouter, Query
from typing import Optional, List
from models.User import User
from config.database import db_dependency
from services.impl.UserServiceImpl import UserServiceImpl
from dto.res.GeneralMsgResDto import GeneralMsgResDto
from dto.res.UserResDto import UserResDto

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get("",
            response_model=List[UserResDto] | UserResDto,
            responses={
                404: {"model": GeneralMsgResDto, "description": "User not found"},
                400: {"model": GeneralMsgResDto, "description": "Bad Request"},
                500: {"model": GeneralMsgResDto, "description": "Internal Server Error"}
            }
            )
async def get_users(
        db: db_dependency,
        username: Optional[str] = Query(None, description="Enter the username to find user with username"),
        email: Optional[str] = Query(None, description="Enter the email to find user with email"),
        user_id: Optional[int] = Query(None, description="Enter the user ID to find user with user_id")
):
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

