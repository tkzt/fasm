from fastapi import Query
from pydantic import BaseModel, Field
from models import BaseDBModelResponse
from models.db.user_role import BaseRole
from models.permissions import Permission


class CreateRoleRequest(BaseRole):
    pass


class BaseRoleResponse(BaseRole, BaseDBModelResponse):
    permissions: Permission = Permission(0)


class UpdateRoleRequest(BaseModel):
    desc: str | None = None
    name: str | None = Field(min_length=1, default=None)
    permissions: int | None = Field(default=0)


class GetRoleRequest(BaseModel):
    page: int = Query(ge=1, default=1)
    size: int = Query(ge=1, default=20)
    query: str = Query(default="")
