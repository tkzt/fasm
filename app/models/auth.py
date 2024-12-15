from typing_extensions import Annotated
from pydantic import BaseModel, Field, StringConstraints


class CreateTokenRequest(BaseModel):
    account: str = Field(min_length=1)
    password: str = Field(min_length=1)


class CreatePhoneTokenRequest(BaseModel):
    trace_id: str = Field(min_length=1)
    verification_code: str = Field(min_length=6)
    phone_num: Annotated[
        str,
        StringConstraints(
            pattern=r"^1[3-9]\d{9}$",
        ),
    ]


class CreateTokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class RefreshTokenResponse(CreateTokenResponse):
    refresh_token: str = Field(exclude=True, default="")


class CaptchaResponse(BaseModel):
    captcha: str
