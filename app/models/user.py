from fastapi import Query
from pydantic import BaseModel, Field
from models import BaseDBModelResponse
from models.db.user_role import BaseUser
from models.role import BaseRoleResponse


class UserProfile(BaseModel):
    pass


class CreateUserRequest(BaseUser):
    pwd: str = Field(min_length=1)


class BaseUserResponse(BaseUser, BaseDBModelResponse):
    profile: UserProfile
    roles: list[BaseRoleResponse] = []


class UpdateUserRequest(BaseModel):
    profile: dict | None = None
    name: str | None = Field(min_length=1, default=None)


class GetUserRequest(BaseModel):
    page: int = Query(ge=1, default=1)
    size: int = Query(ge=1, default=20)
    query: str = Query(default="")


class SelfUserResponse(BaseUserResponse):
    roles: list[BaseRoleResponse] = Field(exclude=True)
    permissions: int = 0
