from fastapi import APIRouter, Depends, Request
from sqlmodel import select

from models.auth import (
    CaptchaResponse,
    CreateTokenRequest,
    CreateTokenResponse,
    RefreshTokenResponse,
)
from models.db.user_role import User
from models.states import InternalError, StateCode

from utils import generate_random_code
from utils.auth import AuthRequired
from utils.captcha import gen_captcha
from utils.response import create_response
from utils.security import create_access_token, create_refresh_token, verify_pwd
from app_globals import redis_util, limiter
from context_vars import request_context_var


router = APIRouter()


@router.post("/tokens")
async def create_token(create_token_request: CreateTokenRequest):
    the_user = await select(User).where(User.name == create_token_request.account)
    if not the_user:
        raise InternalError(StateCode.USER_NOT_FOUND)

    pwd_matched = verify_pwd(create_token_request.password, the_user.pwd_hash)
    if not pwd_matched:
        raise InternalError(StateCode.NOT_AUTHENTICATED)

    return create_response(
        data=CreateTokenResponse(
            access_token=create_access_token(the_user.id),
            refresh_token=create_refresh_token(the_user.id),
        )
    )


@router.put("/tokens")
async def refresh_token(auth: AuthRequired = Depends(AuthRequired)):
    return create_response(
        data=RefreshTokenResponse(
            access_token=create_access_token(auth.current_user.id),
        )
    )


@router.post("/captchas")
@limiter.limit("100/minute")
async def create_captcha(request: Request):
    request_ctx = request_context_var.get()
    random_code = generate_random_code(5)
    captcha = gen_captcha(random_code)
    await redis_util.set_cache(request_ctx.trace_id, random_code, ex=60)

    return create_response(
        data=CaptchaResponse(
            captcha=captcha,
        )
    )
