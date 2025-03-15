import os
import re
from typing import Annotated
from fastapi import APIRouter, Depends, Request
from dto.req.AuthReqDto import AuthReqDto
from dto.req.UserReqDto import UserReqDto
from config.database import db_dependency
from dto.res.AuthResDto import AuthResDto
from services.impl.AuthServiceImpl import AuthServiceImpl
from services.impl.UserServiceImpl import UserServiceImpl
from dto.res.GeneralMsgResDto import GeneralMsgResDto
from dto.res.ErrorResDto import ErrorResDto
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from fastapi import HTTPException
from pydantic import BaseModel


class LogoutResponse(BaseModel):
    details: str


router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(request: Request, token: Annotated[str, Depends(oauth2_bearer)] = None):
    if token is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication token is missing. Please log in to get a valid token."
        )
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=[os.getenv("ALGO")])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")

        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail="Invalid credentials in JWT token. Please log in.")

        return {'username': username, 'user_id': user_id}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired JWT token. Please log in.")


user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/login",
             response_model=AuthResDto,
             responses={
                 400: {"model": GeneralMsgResDto, "description": "Bad Request"},
                 401: {"model": GeneralMsgResDto, "description": "Unauthorized"},
                 500: {"model": GeneralMsgResDto, "description": "Internal Server Error"}
             }
             )
async def login(
        db: db_dependency,
        form_data: OAuth2PasswordRequestForm = Depends()
):
    if not form_data:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message="Please enter all the credentials",
                details=f"Please enter all the credentials",
            ),
            message="Request could not be completed due to an error.",
        )
        return JSONResponse(content=error_res.dict(), status_code=400)
    elif not form_data.username:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message="Please enter email address or username",
                details=f"Please enter email address or username to log in",
            ),
            message="Request could not be completed due to an error.",
        )
        return JSONResponse(content=error_res.dict(), status_code=400)
    elif not form_data.password:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message="Please enter password",
                details=f"Please enter password to log in",
            ),
            message="Request could not be completed due to an error.",
        )
        return JSONResponse(content=error_res.dict(), status_code=400)
    else:
        auth_service = AuthServiceImpl(db)
        return auth_service.login(AuthReqDto(username_or_email=form_data.username, password=form_data.password))


@router.post("/signup",
             response_model=GeneralMsgResDto,
             responses={
                 400: {"model": GeneralMsgResDto, "description": "Bad Request"},
                 500: {"model": GeneralMsgResDto, "description": "Internal Server Error"}
             }
             )
async def create_user(
        db: db_dependency,
        user: UserReqDto,
):
    if not user:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message="Please fill all the fields",
                details=f"Please fill all the required fields",
            ),
            message="Request could not be completed due to an error.",
        )
        return JSONResponse(content=error_res.dict(), status_code=400)
    elif not user.email:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message="Please fill email address",
                details=f"You can not leave email address empty",
            ),
            message="Request could not be completed due to an error.",
        )
        return JSONResponse(content=error_res.dict(), status_code=400)
    elif not user.username:
        error_res = GeneralMsgResDto(
            isSuccess=False,
            hasException=True,
            errorResDto=ErrorResDto(
                code="bad_request",
                message="Please fill username",
                details=f"You can not leave username empty",
            ),
            message="Request could not be completed due to an error.",
        )
        return JSONResponse(content=error_res.dict(), status_code=400)
    elif not user.password:
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
    elif not user.cnf_password:
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

    user_service = UserServiceImpl(db)
    return user_service.add_user(user)


@router.post("/logout",
             response_model=GeneralMsgResDto,
             responses={
                 400: {"model": LogoutResponse, "description": "Bad Request"},
                 401: {"model": LogoutResponse, "description": "Unauthorized"},
                 500: {"model": LogoutResponse, "description": "Internal Server Error"}
             }
             )
async def logout(
        user: user_dependency,
        db: db_dependency,
        token: str = Depends(oauth2_bearer)
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

    auth_service = AuthServiceImpl(db)
    return auth_service.logout(token, user["user_id"])
