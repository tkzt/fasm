from enum import IntEnum
from http import HTTPStatus
from typing import Any


class StateCode(IntEnum):
    def __new__(cls, value: int, message: str, http_code: int):
        state_code = int.__new__(cls, value)
        state_code._value_ = value
        state_code.message = message
        state_code.http_code = http_code
        return state_code

    SUCCESS = 0, "Success", HTTPStatus.OK

    # General exceptions, 1xxx
    UNKNOWN_ERROR = 1000, "Unknown error", HTTPStatus.INTERNAL_SERVER_ERROR
    VALIDATION_ERROR = 1001, "Validation error", HTTPStatus.UNPROCESSABLE_ENTITY
    REQUEST_LIMIT_ERROR = 1002, "Request limit error", HTTPStatus.TOO_MANY_REQUESTS

    # Auth, 2xxx
    NOT_AUTHENTICATED = 2000, "Invalid authentication state", HTTPStatus.UNAUTHORIZED
    AUTHENTICATION_EXPIRED = (
        2001,
        "Authentication state has expired",
        HTTPStatus.UNAUTHORIZED,
    )
    NOT_AUTHORIZED = 2002, "Insufficient permissions", HTTPStatus.FORBIDDEN
    INVALidCAPTCHA = 2003, "Invalid captcha", HTTPStatus.UNPROCESSABLE_ENTITY

    # User & Role, 3xxx
    USER_NOT_FOUND = 3000, "User not found", HTTPStatus.NOT_FOUND
    USER_REPEAT = (
        3001,
        "User with same phone number or name exists",
        HTTPStatus.CONFLICT,
    )
    ROLE_NOT_FOUND = 3002, "Role not found", HTTPStatus.NOT_FOUND
    ROLE_REPEAT = (
        3003,
        "Role with same name exists",
        HTTPStatus.CONFLICT,
    )
    USER_BLOCKED = 3004, "User has been blocked", HTTPStatus.LOCKED


class InternalError(Exception):
    error_code: int
    message: str
    http_status_code: int

    def __init__(
        self,
        error_code: StateCode,
        message: str | None = None,
        http_status_code: int | None = None,
        data: Any | None = None,
    ):
        message = message or error_code.message
        http_status_code = http_status_code or error_code.http_code
        super().__init__(
            message, error_code, http_status_code
        )  # make exception picklable (fill args member)
        self.message = message
        self.error_code = error_code
        self.http_status_code = http_status_code
        self.data = data

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return (
            f'{class_name}(message="{self.message}", error_code={self.error_code}, '
            f"http_status_code={self.http_status_code})"
        )
