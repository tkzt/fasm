from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel
from utils import current_time_seconds


class BaseDBModelWithoutId(SQLModel):
    __table_args__ = {"extend_existing": True}
    updated_at: int = Field(
        default_factory=current_time_seconds,
        sa_column_kwargs={"onupdate": current_time_seconds},
    )
    created_at: int = Field(default_factory=current_time_seconds)
    deleted_at: int | None = Field(None)


class BaseDBModel(BaseDBModelWithoutId):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
