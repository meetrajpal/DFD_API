from starlette.responses import JSONResponse

from dao.InvalidTokenDAO import InvalidTokenDAO
from dto.res.ErrorResDto import ErrorResDto
from dto.res.GeneralMsgResDto import GeneralMsgResDto
from models.InvalidToken import InvalidToken
from services.InvalidTokenService import InvalidTokenService
from sqlalchemy.orm import Session


class InvalidTokenServiceImpl(InvalidTokenService):

    def __init__(self, db: Session):
        self.dao = InvalidTokenDAO(db)

    def expire_token(self, token: str):
        try:
            self.dao.expire_token(InvalidToken(token))
        except Exception as e:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="internal_server_error",
                    message="Error occurred while expiring token.",
                    details=f"Error occurred while expiring token: {e}",
                ),
                message="Request could not be completed due to an error.",
            )
            return JSONResponse(content=error_res.dict(), status_code=500)

    def get_by_token(self, token: str):
        return self.dao.get_invalid_token_by_token(token)
