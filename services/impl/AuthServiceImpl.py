import os
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from dao.UserDAO import UserDAO
from dto.req.AuthReqDto import AuthReqDto
from dto.res.ErrorResDto import ErrorResDto
from dto.res.GeneralMsgResDto import GeneralMsgResDto
from passlib.context import CryptContext
from jose import jwt

from services.AuthService import AuthService

bycrpt = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthServiceImpl(AuthService):
    def __init__(self, db: Session):
        self.dao = UserDAO(db)

    def login(self, creds: AuthReqDto):
        user = self.dao.get_user_by_email(creds.username_or_email)
        if not user:
            user = self.dao.get_user_by_username(creds.username_or_email)
            if not user:
                error_res = GeneralMsgResDto(
                    isSuccess=False,
                    hasException=True,
                    errorResDto=ErrorResDto(
                        code="unauthorized",
                        message="User not found",
                        details=f"Invalid username or email: {creds.username_or_email}",
                    ),
                    message="Request could not be completed due to an error.",
                )
                return JSONResponse(content=error_res.dict(), status_code=401)

        if not bycrpt.verify(creds.password, user.password):
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="unauthorized",
                    message="Invalid password",
                    details=f"Invalid password for: {creds.username_or_email}",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=401)

        data = {'sub': user.username, 'id': user.user_id, 'exp': datetime.now(timezone.utc) + timedelta(minutes=60)}

        return JSONResponse(content={"access_token": jwt.encode(data, os.getenv("JWT_SECRET"), os.getenv("ALGO")), "token_type": "bearer"}, status_code=200)

    def logout(self, token: str, user_id: int):

        success = GeneralMsgResDto(
            isSuccess=True,
            hasException=False,
            message=f"Successfully Logged Out: {token}: {user_id}",
        )
        return JSONResponse(content=success.dict(), status_code=200)
