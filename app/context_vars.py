from contextvars import ContextVar

from models import RequestContext


request_context_var: ContextVar[RequestContext] = ContextVar(
    "request_context_var", default=RequestContext()
)
