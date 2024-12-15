from datetime import datetime
from typing import Generic, TypeVar
from models.states import StateCode
from pydantic import BaseModel

from context_vars import request_context_var

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    trace_id: str
    code: int
    at: str
    message: str
    data: T | None = None


def make_response(
    trace_id: str | None = None,
    data: T | None = None,
    code: int | StateCode | None = None,
    message: str | None = None,
) -> BaseResponse[T]:
    if trace_id is None:
        trace_id = request_context_var.get().trace_id
    if isinstance(data, BaseResponse):
        return data
    if isinstance(code, StateCode):
        message = message or code.message
    return BaseResponse[T](
        code=code or StateCode.SUCCESS,
        trace_id=trace_id,
        data=data,
        at=datetime.isoformat(datetime.now()),
        message=message or StateCode.SUCCESS.message,
    )
