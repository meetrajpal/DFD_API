import os
import re
from typing import Annotated
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
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


router = APIRouter(prefix="/api/v1/webhooks", tags=["Webhooks"])


@router.get("/verify-email/{user_id}",
            response_class=HTMLResponse,
            responses={
                404: {"description": "User not found"},
                400: {"description": "Bad Request"},
                500: {"description": "Internal Server Error"}
            }
            )
async def verify_email(
        db: db_dependency,
        user_id: int
):
    if not user_id:
        return HTMLResponse(content=f'''
            <html>
                <head>
                    <title>Error</title>
                </head>
                <body>
                    <center>
                        <img src="https://s3-cdn.cmlabs.co/page/2023/01/24/a-guideline-on-how-to-fix-error-404-not-found-effectively-519451.png" alt="USER ID NOT FOUND"
                        <h1>
                            USER ID NOT FOUND IN URL
                        </h1>
                    </center>                    
                </body>
            </html>
        ''', status_code=400)

    user_service = UserServiceImpl(db)
    return user_service.verify_email(user_id)
