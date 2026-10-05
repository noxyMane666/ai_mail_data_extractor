import logging

from anthropic import APIConnectionError, APIError, APIStatusError, APITimeoutError
from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        return _handle_http_exception(exc)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        return _handle_validation_exception(exc)

    @app.exception_handler(APIError)
    async def anthropic_exception_handler(request: Request, exc: APIError) -> JSONResponse:
        return _handle_anthropic_exception(exc)

def _handle_http_exception(exc: HTTPException) -> JSONResponse:
    logger.warning(
        "HTTP exception",
        extra={"event": "http_exception", "status_code": exc.status_code, "detail": exc.detail},
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )


def _handle_validation_exception(exc: RequestValidationError) -> JSONResponse:
    error_locations = [".".join(str(part) for part in error["loc"]) for error in exc.errors()]
    logger.warning(
        "Request validation failed",
        extra={"event": "validation_failed", "status_code": 422, "error_locations": error_locations},
    )
    details = jsonable_encoder(exc.errors())

    return JSONResponse(
        status_code=422,
        content={"message": "Validation error", "details": details},
    )


def _handle_anthropic_exception(exc: APIError) -> JSONResponse:
    if isinstance(exc, APITimeoutError):
        logger.error(
            "LLM provider timeout",
            exc_info=exc,
            extra={"event": "llm_provider_timeout", "status_code": 504},
        )
        return JSONResponse(
            status_code=504,
            content={"message": "LLM provider timeout", "details" : exc.message},
        )
    if isinstance(exc, APIConnectionError):
        logger.error(
            "LLM provider connection failed",
            exc_info=exc,
            extra={"event": "llm_provider_connection_failed", "status_code": 502},
        )
        return JSONResponse(
            status_code=502,
            content={"message": "Couldn't connect to LLM provider", "details" : exc.message},
        )
    if isinstance(exc, APIStatusError):
        logger.error(
            "LLM provider returned an error",
            exc_info=exc,
            extra={"event": "llm_provider_error", "status_code": 502, "provider_status_code": exc.status_code},
        )
        return JSONResponse(
            status_code=502,
            content={"message": "LLM provider error", "details": exc.message},
        )

    logger.error(
        "Unexpected LLM client error",
        exc_info=exc,
        extra={"event": "llm_unexpected_error", "status_code": 500},
    )
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error"},
    )
