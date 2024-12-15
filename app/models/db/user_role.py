from uuid import UUID
from models.db import BaseDBModel, BaseDBModelWithoutId
from models.permissions import Permission
from sqlmodel import (
    Field,
    Relationship,
    SQLModel,
    Column,
    UUID as SM_UUID,
    ForeignKey,
    JSON,
    Integer,
)


ADMIN_USER_NAME = "admin"
DEFAULT_ROLE_NAME = "Default"


class UserRole(BaseDBModelWithoutId, table=True):
    __tablename__ = "user_role"
    user_id: UUID = Field(
        sa_column=Column(
            SM_UUID,
            ForeignKey("user.id", ondelete="CASCADE"),
            primary_key=True,
        )
    )
    role_id: UUID = Field(
        sa_column=Column(
            SM_UUID,
            ForeignKey("role.id", ondelete="CASCADE"),
            primary_key=True,
        )
    )


class BaseUser(SQLModel):
    name: str = Field(min_length=1, unique=True)


class User(BaseUser, BaseDBModel, table=True):
    pwd_hash: str | None = Field(default=None)
    is_active: bool = True
    is_admin: bool = False
    profile: dict = Field(sa_column=Column(JSON, default={}))
    roles: list["Role"] = Relationship(link_model=UserRole, back_populates="users")


class BaseRole(SQLModel):
    name: str = Field(unique=True)
    desc: str = ""


class Role(BaseRole, BaseDBModel, table=True):
    permissions: Permission = Field(sa_column=Column(Integer, default=0))
    users: list["User"] = Relationship(link_model=UserRole, back_populates="roles")
