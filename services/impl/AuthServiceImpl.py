from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from dao.UserDAO import UserDAO
from dto.req.AuthReqDto import AuthReqDto
from dto.res.ErrorResDto import ErrorResDto
from dto.res.GeneralMsgResDto import GeneralMsgResDto
from passlib.context import CryptContext
from jose import jwt
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from services.AuthService import AuthService
from config.MailTemplate import *
from services.impl.InvalidTokenServiceImpl import InvalidTokenServiceImpl

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = os.getenv('BREVO')
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
bycrpt = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthServiceImpl(AuthService):
    def __init__(self, db: Session):
        self.db = db
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

        data = {'sub': user.username, 'id': user.user_id, 'iat': datetime.now(timezone.utc),
                'exp': datetime.now(timezone.utc) + timedelta(minutes=60)}

        return JSONResponse(content={"access_token": jwt.encode(data, os.getenv("JWT_SECRET"), os.getenv("ALGO")),
                                     "token_type": "bearer"}, status_code=200)

    def logout(self, token: str, **kwargs):
        invalid_token_service = InvalidTokenServiceImpl(self.db)
        invalid_token_service.expire_token(token)
        success = GeneralMsgResDto(
            isSuccess=True,
            hasException=False,
            message=f"Successfully Logged Out",
        )
        return JSONResponse(content=success.dict(), status_code=200)

    def forgot_password(self, email: str):
        user_data = self.dao.get_user_by_email(email)
        if not user_data:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="not_found",
                    message="User not found",
                    details=f"User not found with given email: {email}",
                ),
                message="Request could not be completed due to an error."
            )
            return JSONResponse(content=error_res.dict(), status_code=404)

        data = {'sub': user_data.username, 'id': user_data.user_id, 'tokenType': "forgot_password", 'iat': datetime.now(timezone.utc),
                'exp': datetime.now(timezone.utc) + timedelta(minutes=15)}

        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail()
        send_smtp_email.subject = "Reset Password"
        send_smtp_email.html_content = generate_forgot_password_email_template(jwt.encode(data, os.getenv("JWT_SECRET"), os.getenv("ALGO")))
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
                    message="Error occurred while forget password.",
                    details=f"Error occurred while sending email verification for forgot password.: {e}",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=500)

        success = GeneralMsgResDto(
            isSuccess=True,
            hasException=False,
            message="Email sent with password reset link.",
        )
        return JSONResponse(content=success.dict(), status_code=200)

    def update_email(self, email: str):
        user_data = self.dao.get_user_by_email(email)
        if not user_data:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="not_found",
                    message="User not found",
                    details=f"User not found with given email: {email}",
                ),
                message="Request could not be completed due to an error."
            )
            return JSONResponse(content=error_res.dict(), status_code=404)

        data = {'sub': user_data.username, 'id': user_data.user_id, 'tokenType': "update_email", 'iat': datetime.now(timezone.utc),
                'exp': datetime.now(timezone.utc) + timedelta(minutes=15)}

        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail()
        send_smtp_email.subject = "Update Email"
        send_smtp_email.html_content = generate_update_email_template(jwt.encode(data, os.getenv("JWT_SECRET"), os.getenv("ALGO")))
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
                    message="Error occurred while updating email.",
                    details=f"Error occurred while sending email verification for update email.: {e}",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=500)

        success = GeneralMsgResDto(
            isSuccess=True,
            hasException=False,
            message="Email sent with email update link.",
        )
        return JSONResponse(content=success.dict(), status_code=200)
