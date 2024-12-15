import time
from typing import TypeVar
import jwt
from fastapi import Depends, Security
from fastapi.params import Depends as Dependency
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi_async_sqlalchemy import db
from sqlmodel import select

from models.states import InternalError, StateCode
from models.db.user_role import User
from models.permissions import Permission
from utils.security import verify_jwt
from utils.logger import logger
from context_vars import request_context_var

UUIDStr = TypeVar("UUIDStr", bound=str)
bearer_token = HTTPBearer(auto_error=False)


def verify_token(token: HTTPAuthorizationCredentials) -> UUIDStr:
    """
    Verify a bearer token.

    Parameters
    ----------
    token:
        A HTTPAuthorizationCredentials object resolved from header `Authorization`,
        whose value is like `Bearer ${one_jwt}`.

    Returns
    -------
    ID of current user
    """
    try:
        if not token or token.scheme.lower() != "bearer":
            logger.error("Invalid credentials")
            raise InternalError(error_code=StateCode.NOT_AUTHENTICATED)
        return verify_jwt(token.credentials).get("sub")
    except jwt.ExpiredSignatureError:
        logger.error("Token has been expired")
        raise InternalError(error_code=StateCode.AUTHENTICATION_EXPIRED)
    except jwt.PyJWTError:
        logger.error("Invalid Token")
        raise InternalError(error_code=StateCode.NOT_AUTHENTICATED)


async def authenticate(
    token: HTTPAuthorizationCredentials = Security(bearer_token),
) -> User:
    st = time.time()
    user_id = verify_token(token)

    if not user_id:
        raise InternalError(error_code=StateCode.USER_NOT_FOUND)

    current_user = await db.session.scalar(select(User).where(User.id == user_id))
    request_ctx = request_context_var.get()
    request_ctx.current_user = current_user
    logger.debug(f"Time taken for authenticating: {time.time() - st}s")

    if not current_user:
        raise InternalError(error_code=StateCode.USER_NOT_FOUND)
    if not current_user.is_active:
        raise InternalError(error_code=StateCode.USER_BLOCKED)

    await db.session.refresh(request_ctx.current_user, attribute_names=["wallets"])
    active_wallets = [
        wallet for wallet in request_ctx.current_user.wallets if wallet.is_active
    ]
    request_ctx.current_wallet = active_wallets[0] if len(active_wallets) else None

    return current_user


class AuthRequired:
    """Generally speaking:
    ### route requires sign-in state only
    @router.get("/foo", dependencies=[Depends(AuthRequired)])
    def foo():
        ...

    ### or
    @router.get("/foo")
    def foo(auth: AuthRequired = Depends(AuthRequired)):
        # in which case we can get an object with a useful property `current_user`
        ...

    ### and route requires some permissions
    @router.get(
        "/bar",
        dependencies=[Depends(AuthRequired([Permission.SYSTEM, Permission.BAR]))]
    )
    def bar():
        ...

    ### or
    @router.get("/bar")
    def bar(
        auth: AuthRequired = Depends(AuthRequired([Permission.SYSTEM, Permission.BAR]))
    ):
        ...
    """

    def __init__(
        self,
        required_permissions: list[Permission] | None = Depends(lambda: None),
        current_user: User | None = Depends(authenticate),
    ):
        self.current_user = current_user
        self.required_permissions = required_permissions

        # We use `Depends` to avoid Fastapi from retrieving body (
        #   mainly because `required_permissions` is a list instead of a basic type),
        #   in situation `AuthRequired` used like this:
        #   ```
        #   def some_route_func(auth: AuthRequired = Depends(AuthRequired)):
        #       ...
        #   ```
        # But when it's used like:
        #   ```
        #   def some_route_func(auth: AuthRequired = Depends(AuthRequired)):
        #       ...
        #   ```
        # What we then get from `required_permissions`
        #   is an empty `fastapi.params.Depends`,
        # we have to handle it specially.
        if isinstance(required_permissions, Dependency):
            self.required_permissions = None

    async def __call__(
        self,
        current_user: User = Depends(authenticate),
    ):  # require some permissions
        self.current_user = current_user
        await db.session.refresh(self.current_user, attribute_names=["roles"])

        authorized_permissions = Permission(0)
        for role in current_user.roles:
            authorized_permissions |= role.permission or Permission(0)

        # an authorization checking result
        if current_user.is_admin or (
            not self.required_permissions
            or any(
                [
                    (permission & authorized_permissions == permission)
                    for permission in self.required_permissions
                ]
            )
        ):
            return self
        raise InternalError(error_code=StateCode.NOT_AUTHORIZED)
