from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from dao.UserDAO import UserDAO
from dto.req.UserReqDto import UserReqDto
from dto.res.ErrorResDto import ErrorResDto
from dto.res.GeneralMsgResDto import GeneralMsgResDto
from models.User import User
from passlib.context import CryptContext
import traceback

from services.UserService import UserService

bycrpt = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserServiceImpl(UserService):
    def __init__(self, db: Session):
        self.dao = UserDAO(db)

    def get_users(self):
        return self.dao.get_all_users()

    def get_user_by_id(self, user_id: int):
        user = self.dao.get_user_by_id(user_id)
        if user is None:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="not_found",
                    message="User not found",
                    details=f"User not found with user_id: {user_id}",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=404)
        return user

    def get_user_by_email(self, email: str):
        user = self.dao.get_user_by_email(email)
        if user is None:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="not_found",
                    message="User not found",
                    details=f"User not found with email: {email}",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=404)
        return user

    def get_user_by_username(self, username: str):
        user = self.dao.get_user_by_username(username)
        if user is None:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="not_found",
                    message="User not found",
                    details="User not found with username: " + username,
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=404)
        return user

    def get_user_by_multiple_filters(self, filters: list):
        users = self.dao.get_user_by_multiple_filters(filters)
        if len(users) == 0:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="not_found",
                    message="User not found",
                    details=f"User not found with given filters.",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=404)
        return users

    def add_user(self, user: UserReqDto):
        data = self.dao.get_user_by_username(user.username)
        if data is not None and data.username == user.username:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="bad_request",
                    message="User already exists",
                    details=f"User already exists with username: {user.username}",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=400)
        data = self.dao.get_user_by_email(user.email)
        if data is not None and data.email == user.email:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="bad_request",
                    message="Email already exists",
                    details=f"This email is already in use: {user.email}",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=400)

        new_user = User(user.username, user.name, user.email, bycrpt.hash(user.password))
        try:
            self.dao.create_user(new_user)
        except Exception:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="internal_server_error",
                    message="Error occurred while creating user.",
                    details=f"Error occurred while creating user: {traceback.print_exc()}",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=500)

        success = GeneralMsgResDto(
            isSuccess=True,
            hasException=False,
            message="User signed up successfully.",
        )
        return JSONResponse(content=success.dict(), status_code=200)
