import os
from fastapi import HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from dao.UserDAO import UserDAO
from dto.req.UserReqDto import UserReqDto
from dto.res.ErrorResDto import ErrorResDto
from dto.res.GeneralMsgResDto import GeneralMsgResDto
from models.User import User
from passlib.context import CryptContext
import traceback
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from services.UserService import UserService
from config.MailTemplate import generate_verify_email_template
from jose import jwt, JWTError
from datetime import datetime, timezone
from services.impl.InvalidTokenServiceImpl import InvalidTokenServiceImpl

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = os.getenv('BREVO')
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

bycrpt = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserServiceImpl(UserService):
    def __init__(self, db: Session):
        self.db = db
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
                    message="Username already exists",
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

        try:
            new_user = self.dao.create_user(User(user.username, user.name, user.email, bycrpt.hash(user.password)))
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

        data = {'sub': new_user.username, 'id': new_user.user_id, 'tokenType': "verify_email", 'iat': datetime.now(timezone.utc)}

        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail()
        send_smtp_email.subject = "Account Email Verification"
        send_smtp_email.html_content = generate_verify_email_template(jwt.encode(data, os.getenv("JWT_SECRET"), os.getenv("ALGO")))
        send_smtp_email.sender = {"name": "no-reply", "email": "dfd.onrender@gmail.com"}
        send_smtp_email.to = [{"email": user.email}]

        try:
            api_response = api_instance.send_transac_email(send_smtp_email)
            print(api_response)
        except ApiException as e:
            self.dao.delete_user(new_user)
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="internal_server_error",
                    message="Error occurred while creating new user.",
                    details=f"Error occurred while sending email verification for creating new user.: {e}",
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

    def verify_email(self, token: str):
        try:
            payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=[os.getenv("ALGO")])
            username: str = payload.get("sub")
            user_id: int = payload.get("id")
            token_type: str = payload.get("tokenType")
            print(username)
            print(user_id)
            print(token_type)
            if username is None or user_id is None or token_type is None or token_type != "verify_email":
                raise HTTPException(status_code=401, detail="Invalid credentials in JWT token while verifying email.")
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid or expired JWT token while verifying email.")

        user_data = self.dao.get_user_by_id(user_id)
        if not user_data or user_data.username != username:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="not_found",
                    message="User not found",
                    details=f"User not found with user_id: {user_id} while verifying email.",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=404)
        else:
            if self.dao.verify_user_email(user_id):
                # < script src = "https://unpkg.com/@dotlottie/player-component@2.7.12/dist/dotlottie-player.mjs" type = "module" > < / script >
                # < dotlottie - player
                # src = "https://lottie.host/0a080f91-0c78-4520-b708-880761670d4e/xOioiVRJzw.lottie"
                # background = "transparent"
                # speed = "1"
                # style = "width: 300px; height: 300px"
                # loop
                # autoplay > < / dotlottie - player >

                invalid_token_service = InvalidTokenServiceImpl(self.db)
                invalid_token_service.expire_token(token)

                success = GeneralMsgResDto(
                    isSuccess=True,
                    hasException=False,
                    message="Email verified successfully.",
                )
                return JSONResponse(content=success.dict(), status_code=200)
            else:
                error_res = GeneralMsgResDto(
                    isSuccess=False,
                    hasException=True,
                    errorResDto=ErrorResDto(
                        code="internal_server_error",
                        message="Something went wrong.",
                        details=f"Internal server error occurred while verifying email.",
                    ),
                    message="Request could not be completed due to an error.",
                )
                return JSONResponse(content=error_res.dict(), status_code=500)

    def reset_password(self, token: str, password: str):
        try:
            payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=[os.getenv("ALGO")])
            username: str = payload.get("sub")
            user_id: int = payload.get("id")
            token_type: str = payload.get("tokenType")
            if username is None or user_id is None or token_type is None or token_type != "forgot_password":
                raise HTTPException(status_code=401, detail="Invalid credentials in JWT token while resetting password.")
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid or expired JWT token while resetting password.")

        user_data = self.dao.get_user_by_id(user_id)
        if not user_data or user_data.username != username:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="not_found",
                    message="User not found",
                    details=f"User not found with user_id: {user_id} while resetting password.",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=404)
        else:
            if self.dao.update_user_password(user_id, bycrpt.hash(password)):

                invalid_token_service = InvalidTokenServiceImpl(self.db)
                invalid_token_service.expire_token(token)

                success = GeneralMsgResDto(
                    isSuccess=True,
                    hasException=False,
                    message="Password changed successfully.",
                )
                return JSONResponse(content=success.dict(), status_code=200)
            else:
                error_res = GeneralMsgResDto(
                    isSuccess=False,
                    hasException=True,
                    errorResDto=ErrorResDto(
                        code="internal_server_error",
                        message="Something went wrong.",
                        details=f"Internal server error occurred while resetting password.",
                    ),
                    message="Request could not be completed due to an error.",
                )
                return JSONResponse(content=error_res.dict(), status_code=500)

    def update_email(self, token: str, email: str):
        try:
            payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=[os.getenv("ALGO")])
            username: str = payload.get("sub")
            user_id: int = payload.get("id")
            token_type: str = payload.get("tokenType")
            if username is None or user_id is None or token_type is None or token_type != "update_email":
                raise HTTPException(status_code=401, detail="Invalid credentials in JWT token while updating email.")
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid or expired JWT token while updating email.")

        user_data = self.dao.get_user_by_id(user_id)
        if not user_data or user_data.username != username:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="not_found",
                    message="User not found",
                    details=f"User not found with user_id: {user_id} while updating email.",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=404)
        else:
            if self.dao.update_user_email(user_id, email):
                data = {'sub': user_data.username, 'id': user_data.user_id, 'tokenType': "verify_email", 'iat': datetime.now(timezone.utc)}

                send_smtp_email = sib_api_v3_sdk.SendSmtpEmail()
                send_smtp_email.subject = "Account Email Verification"
                send_smtp_email.html_content = generate_verify_email_template(
                    jwt.encode(data, os.getenv("JWT_SECRET"), os.getenv("ALGO")))
                send_smtp_email.sender = {"name": "no-reply", "email": "dfd.onrender@gmail.com"}
                send_smtp_email.to = [{"email": email}]

                try:
                    api_response = api_instance.send_transac_email(send_smtp_email)
                    print(api_response)
                except ApiException as e:
                    error_res = GeneralMsgResDto(
                        isSuccess=False,
                        hasException=True,
                        errorResDto=ErrorResDto(
                            code="internal_server_error",
                            message="Error occurred while creating new user.",
                            details=f"Error occurred while sending email verification for updating email.: {e}",
                        ),
                        message="Request could not be completed due to an error.",
                    )
                    return JSONResponse(content=error_res.dict(), status_code=500)

                invalid_token_service = InvalidTokenServiceImpl(self.db)
                invalid_token_service.expire_token(token)

                success = GeneralMsgResDto(
                    isSuccess=True,
                    hasException=False,
                    message="Email changed successfully.",
                )
                return JSONResponse(content=success.dict(), status_code=200)
            else:
                error_res = GeneralMsgResDto(
                    isSuccess=False,
                    hasException=True,
                    errorResDto=ErrorResDto(
                        code="internal_server_error",
                        message="Something went wrong.",
                        details=f"Internal server error occurred while updating email.",
                    ),
                    message="Request could not be completed due to an error.",
                )
                return JSONResponse(content=error_res.dict(), status_code=500)

    def delete_user(self, user_id: int):
        user = self.dao.get_user_by_id(user_id)
        if not user:
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

        try:
            self.dao.delete_user(user)
        except Exception as e:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="internal_server_error",
                    message="Error occurred while deleting user.",
                    details=f"Error occurred while deleting user: {e}",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=500)

        success = GeneralMsgResDto(
            isSuccess=True,
            hasException=False,
            message="User deleted successfully.",
        )
        return JSONResponse(content=success.dict(), status_code=200)
