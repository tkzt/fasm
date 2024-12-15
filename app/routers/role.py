from uuid import UUID
from fastapi import APIRouter, Depends
from fastapi_async_sqlalchemy import db
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlmodel import paginate
from sqlalchemy.exc import IntegrityError
from sqlmodel import or_, select

from models.db.user_role import Role
from models.permissions import Permission
from models.role import (
    BaseRoleResponse,
    CreateRoleRequest,
    GetRoleRequest,
    UpdateRoleRequest,
)
from models.states import InternalError, StateCode
from utils.auth import AuthRequired
from utils.response import create_response


router = APIRouter(
    prefix="/roles", dependencies=[Depends(AuthRequired(Permission.SYSTEM))]
)


@router.post("")
async def create_role(create_role_request: CreateRoleRequest):
    try:
        new_role = Role(
            name=create_role_request.name,
            desc=create_role_request.desc,
        )
        db.session.add(new_role)
        await db.session.commit()
    except IntegrityError as err:
        if "UniqueViolationError" in str(err):
            raise InternalError(StateCode.ROLE_REPEAT)
    return create_response(data=BaseRoleResponse.model_validate(obj=new_role))


@router.patch("/{role_id}")
async def update_role(update_role_request: UpdateRoleRequest, role_id: UUID):
    try:
        the_role = await db.session.scalar(select(Role).where(Role.id == role_id))
        if not the_role:
            raise InternalError(StateCode.ROLE_NOT_FOUND)
        for attr in (update_dict := update_role_request.model_dump(exclude_none=True)):
            setattr(the_role, attr, update_dict[attr])
        await db.session.commit()
    except IntegrityError as err:
        if "UniqueViolationError" in str(err):
            raise InternalError(StateCode.ROLE_REPEAT)
    return create_response(data=BaseRoleResponse.model_validate(the_role))


@router.get("")
async def get_roles(get_role_request: GetRoleRequest = Depends()):
    query_pattern = f"%{get_role_request.query}%"
    res_paginated = await paginate(
        db.session,
        (
            select(Role).where(
                or_(Role.name.ilike(query_pattern), Role.desc.ilike(query_pattern))
            )
            if get_role_request.query
            else select(Role)
        ).order_by(Role.updated_at.desc()),
        Params(page=get_role_request.page, size=get_role_request.size),
        transformer=lambda x: [BaseRoleResponse.model_validate(role) for role in x],
    )
    return create_response(data=res_paginated)
