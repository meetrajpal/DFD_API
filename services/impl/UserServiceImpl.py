import os
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse, HTMLResponse
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
from config.MailTemplate import generate_email_template

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = os.getenv('BREVO')
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
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

        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail()
        send_smtp_email.subject = "Account Email Verification"
        send_smtp_email.html_content = generate_email_template(new_user.user_id)
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

    def verify_email(self, user_id: int):
        user_data = self.dao.get_user_by_id(user_id)
        if not user_data:
            return HTMLResponse(content=f'''
                        <html>
                            <head>
                                <title>Error</title>
                            </head>
                            <body>
                                <center style="background-color:#1f95f5; color:white; max-width:100%;">
                                    <h1>
                                        USER NOT FOUND FOR GIVEN ID {user_id}
                                    </h1>
                                    <img width=100% src="https://s3-cdn.cmlabs.co/page/2023/01/24/a-guideline-on-how-to-fix-error-404-not-found-effectively-519451.png" alt="USER ID NOT FOUND"
                                </center>                    
                            </body>
                        </html>
                    ''', status_code=404)
        else:
            if self.dao.verify_user_email(user_id):
                return HTMLResponse(content=f'''
                            <html>
                                <head>
                                    <title>Verified</title>
                                    <script src="https://unpkg.com/@dotlottie/player-component@2.7.12/dist/dotlottie-player.mjs" type="module"></script>
                                    <style type="text/css">
                                        a {{ text-decoration: none !important; color: #0000EE; }}
                                        p {{ font-size: 15px; line-height: 24px; font-family: 'Helvetica', Arial, sans-serif; color: #000000; }}
                                        h1 {{ font-size: 22px; font-family: 'Helvetica', Arial, sans-serif; color: #000000; }}
                                    </style>
                                </head>
                                <body>
                                    <center>
                                        <dotlottie-player src="https://lottie.host/0a080f91-0c78-4520-b708-880761670d4e/xOioiVRJzw.lottie" background="transparent" speed="1" style="width: 300px; height: 300px" loop autoplay></dotlottie-player>
                                        </br>
                                        <h1>
                                            Your email address has been verified successfully.
                                        </h1>
                                        </br>
                                        <a href="{os.getenv("FRONT_DOMAIN")}" style="background-color: #000000; padding: 12px 15px; color: #ffffff; border-radius: 25px;">GO TO HOME</a>
                                    </center>                    
                                </body>
                            </html>
                        ''', status_code=200)
            else:
                return HTMLResponse(content=f'''
                            <html>
                                <head>
                                    <title>Error</title>
                                </head>
                                <body>
                                    <center>
                                        <h1>
                                            INTERNAL SERVER OCCURRED
                                        </h1>
                                    </center>                    
                                </body>
                            </html>
                        ''', status_code=500)

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
