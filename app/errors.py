import logging
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("uvicorn.error")  # prints in the terminal that runs uvicorn


class AppError(Exception):
    """Base class for errors we raise on purpose."""

    status_code = 400
    code = "bad_request"

    def __init__(self, message: str):
        self.message = message


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"

    def __init__(self, what: str):
        super().__init__(f"{what} not found")


class FileTooLargeError(AppError):
    status_code = 413
    code = "file_too_large"

    def __init__(self, limit_bytes: int):
        super().__init__(f"The file is larger than {limit_bytes // (1024 * 1024)} MB")


class UnsupportedFileTypeError(AppError):
    status_code = 415
    code = "unsupported_file_type"

    def __init__(self, allowed: str):
        super().__init__(f"This file type is not allowed. Allowed types: {allowed}")


def error_response(status_code: int, code: str, message, headers=None, **extra):
    body = {"error": {"code": code, "message": message, **extra}}
    return JSONResponse(status_code=status_code, content=body, headers=headers)


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return error_response(exc.status_code, exc.code, exc.message)

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(request: Request, exc: StarletteHTTPException):
        try:
            code = HTTPStatus(exc.status_code).name.lower()
        except ValueError:
            code = "error"
        return error_response(exc.status_code, code, exc.detail, headers=exc.headers)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        fields = [
            {
                "in": err["loc"][0],
                "field": ".".join(str(part) for part in err["loc"][1:]),
                "message": err["msg"],
            }
            for err in exc.errors()
        ]
        return error_response(422, "validation_error", "Request is not valid", fields=fields)

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        return error_response(409, "conflict", "A record with this value already exists")

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception):
        logger.error("Unhandled error on %s %s", request.method, request.url.path, exc_info=exc)
        return error_response(500, "internal_error", "Something went wrong on our side")
