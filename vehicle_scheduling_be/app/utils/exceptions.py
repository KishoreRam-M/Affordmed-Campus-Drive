from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(self, message: str, status_code: int) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ExternalAPIError(AppError):
    def __init__(self, message: str = "External evaluation service failed") -> None:
        super().__init__(message=message, status_code=status.HTTP_502_BAD_GATEWAY)


class ExternalAPITimeoutError(AppError):
    def __init__(self, message: str = "External evaluation service timed out") -> None:
        super().__init__(message=message, status_code=status.HTTP_504_GATEWAY_TIMEOUT)


class DepotNotFoundError(AppError):
    def __init__(self, depot_id: str) -> None:
        super().__init__(
            message=f"Depot '{depot_id}' was not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class InvalidDepotError(AppError):
    def __init__(self, depot_id: str) -> None:
        super().__init__(
            message=f"Depot '{depot_id}' has invalid or missing mechanic hours",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


def error_payload(message: str, details: Any | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"error": message}
    if details is not None:
        payload["details"] = details
    return payload


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=error_payload(exc.message),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_payload("Request validation failed", exc.errors()),
        )

    @app.exception_handler(Exception)
    async def unexpected_error_handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_payload("Internal server error"),
        )

