from pydantic import BaseModel

from app.schemas.base import BaseDTO


class AccessTokenDTO(BaseDTO):
    access_token: str
    token_type: str