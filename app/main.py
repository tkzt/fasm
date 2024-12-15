from http import HTTPStatus
import json
import time
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi_async_sqlalchemy import SQLAlchemyMiddleware
from fastapi.middleware.cors import CORSMiddleware
from models import RequestContext
from models.states import StateCode, InternalError
from sqlalchemy import AsyncAdaptedQueuePool
from slowapi.errors import RateLimitExceeded

from utils.response import make_response
from settings import settings
from utils.logger import setup_logger, logger
from routers import base_router
from context_vars import request_context_var
from app_globals import limiter
from init_db import init as init_db

app = FastAPI()
app.include_router(base_router)
LOG_PREFIX = f"{'-'*4}>"
app.state.limiter = limiter


# startup events
app.add_event_handler("startup", setup_logger)
app.add_event_handler("startup", init_db)

# middlewares
app.add_middleware(
    SQLAlchemyMiddleware,
    db_url=str(settings.POSTGRES_DB_URI),
    engine_args={
        "echo": settings.DATABASE_ECHO,
        "max_overflow": settings.DATABASE_MAX_OVERFLOW,
        "poolclass": AsyncAdaptedQueuePool,
    },
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def generic_request(request: Request, call_next):
    start_time = time.time()
    trace_id = str(uuid4())
    request.state.trace_id = trace_id
    request_context_var.set(RequestContext(trace_id=trace_id))

    with logger.contextualize(trace_id=request.state.trace_id):
        response = await call_next(request)
        logger.debug(f"Response code: {response}.")
        process_time = round((time.time() - start_time) * 1000, 2)
        logger.info(
            f"Request: {request.method} {request.url} handled. \n"
            f"{LOG_PREFIX} Status code: {response.status_code}\n"
            f"{LOG_PREFIX} Time taken: {process_time}ms."
        )
        response.headers["x-time-taken"] = str(process_time)
        response.headers["x-trace-id"] = request.state.trace_id
        return response


async def _log_error_request(
    request: Request, exception, exception_name: str | None = None
):
    """Log request details when exceptions occur."""
    trace_id = getattr(request.state, "trace_id", None)
    if not exception_name:
        exception_name = "exception_handler"
    logger.error(f"({exception_name}) Error: {str(exception)}")
    logger.error(
        f"({exception_name}) Request details: \n"
        f"{LOG_PREFIX} Trace ID: {trace_id}.\n"
        f"{LOG_PREFIX} Method: {request.method}, URL: {request.url}.\n"
        f"{LOG_PREFIX} Headers: {request.headers}.\n"
    )
    logger.exception(exception)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_exception_handler(
    request: Request, exception: RateLimitExceeded
):
    await _log_error_request(
        request, exception, "rate_limit_exceeded_exception_handler"
    )
    return JSONResponse(
        status_code=HTTPStatus.TOO_MANY_REQUESTS,
        content=json.loads(
            make_response(
                request.state.trace_id,
                data=str(exception),
                code=StateCode.REQUEST_LIMIT_ERROR,
            ).model_dump_json(exclude_none=True)
        ),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exception: RequestValidationError
):
    await _log_error_request(request, exception, "http_validation_exception_handler")
    return JSONResponse(
        status_code=HTTPStatus.BAD_REQUEST,
        content=json.loads(
            make_response(
                request.state.trace_id,
                data=exception.errors(),
                code=StateCode.VALIDATION_ERROR,
            ).model_dump_json(exclude_none=True)
        ),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exception: HTTPException):
    await _log_error_request(request, exception, "http_exception_handler")
    exception_response = JSONResponse(
        status_code=exception.status_code,
        content=make_response(
            request.state.trace_id,
            data=None,
            code=StateCode.INTERNAL_ERROR,
            message=exception.detail,
        ).model_dump(exclude_none=True),
    )
    if exception.headers:
        exception_response.headers.update(exception.headers)
    return exception_response


@app.exception_handler(InternalError)
async def turing_exception_handler(request: Request, exception: InternalError):
    await _log_error_request(request, exception, "turing_exception_handler")
    return JSONResponse(
        status_code=exception.http_status_code,
        content=json.loads(
            make_response(
                request.state.trace_id,
                data=exception.data,
                code=exception.error_code,
                message=exception.message,
            ).model_dump_json(exclude_none=True)
        ),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exception: Exception):
    await _log_error_request(request, exception, "general_exception_handler")
    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content=make_response(
            request.state.trace_id,
            data=None,
            code=StateCode.UNKNOWN_ERROR,
        ).model_dump(exclude_none=True),
    )
