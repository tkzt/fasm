from uuid import UUID
from pydantic import BaseModel

from models.db.user_role import User


class RequestContext(BaseModel):
    current_user: User | None = None
    trace_id: str | None = None


class BaseDBModelResponse(BaseModel):
    id: UUID
    updated_at: int
    created_at: int
    deleted_at: int | None = None
