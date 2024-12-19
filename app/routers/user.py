from uuid import UUID
from fastapi import APIRouter, Depends
from fastapi_async_sqlalchemy import db
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlmodel import paginate
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from models.db.user_role import User
from models.permissions import ALL_PERMISSIONS, Permission
from models.states import InternalError, StateCode
from models.user import (
    CreateUserRequest,
    BaseUserResponse,
    GetUserRequest,
    SelfUserResponse,
    UpdateUserRequest,
)
from utils.auth import AuthRequired
from utils.response import make_response
from utils.security import gen_pwd_hash
from context_vars import request_context_var


router = APIRouter(prefix="/users", dependencies=[Depends(AuthRequired)])


@router.post("", dependencies=[Depends(AuthRequired(Permission.SYSTEM))])
async def create_user(create_user_request: CreateUserRequest):
    try:
        new_user = User(
            name=create_user_request.name,
            pwd_hash=gen_pwd_hash(create_user_request.pwd),
        )
        db.session.add(new_user)
        await db.session.commit()
    except IntegrityError as err:
        if "UniqueViolationError" in str(err):
            raise InternalError(StateCode.USER_REPEAT)
    return make_response(data=BaseUserResponse.model_validate(new_user))


@router.patch("/{user_id}", dependencies=[Depends(AuthRequired(Permission.SYSTEM))])
async def update_user(update_user_request: UpdateUserRequest, user_id: UUID):
    try:
        the_user = await db.session.scalar(select(User).where(User.id == user_id))
        if not the_user:
            raise InternalError(StateCode.USER_NOT_FOUND)
        for attr in (update_dict := update_user_request.model_dump(exclude_none=True)):
            setattr(the_user, attr, update_dict[attr])
        await db.session.commit()
    except IntegrityError as err:
        if "UniqueViolationError" in str(err):
            raise InternalError(StateCode.USER_REPEAT)
    return make_response(data=BaseUserResponse.model_validate(the_user))


@router.get("", dependencies=[Depends(AuthRequired(Permission.SYSTEM))])
async def get_users(get_user_request: GetUserRequest = Depends()):
    query_pattern = f"%{get_user_request.query}%"
    res_paginated = await paginate(
        db.session,
        (
            select(User).where(User.name.ilike(query_pattern))
            if get_user_request.query
            else select(User)
        ).order_by(User.updated_at.desc()),
        Params(page=get_user_request.page, size=get_user_request.size),
        transformer=lambda x: [BaseUserResponse.model_validate(user) for user in x],
    )
    return make_response(data=res_paginated)


@router.get("/me")
async def get_self_info():
    request_ctx = request_context_var.get()
    await db.session.refresh(request_ctx.current_user, attribute_names=["roles"])
    current_user = SelfUserResponse.model_validate(request_ctx.current_user)

    if request_ctx.current_user.is_admin:
        current_user.permissions = ALL_PERMISSIONS
    else:
        for role in current_user.roles:
            current_user.permissions |= role.permission

    return make_response(data=current_user)
