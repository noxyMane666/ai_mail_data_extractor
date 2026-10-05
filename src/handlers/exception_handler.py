from anthropic import APIConnectionError, APIError, APIStatusError, APITimeoutError
from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


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
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )


def _handle_validation_exception(exc: RequestValidationError) -> JSONResponse:
    details = jsonable_encoder(exc.errors())

    return JSONResponse(
        status_code=422,
        content={"message": "Validation error", "details": details},
    )


def _handle_anthropic_exception(exc: APIError) -> JSONResponse:
    if isinstance(exc, APITimeoutError):
        return JSONResponse(
            status_code=504,
            content={"message": "LLM provider timeout", "details" : exc.message},
        )
    if isinstance(exc, APIConnectionError):
        return JSONResponse(
            status_code=502,
            content={"message": "Couldn't connect to LLM provider", "details" : exc.message},
        )
    if isinstance(exc, APIStatusError):
        return JSONResponse(
            status_code=502,
            content={"message": "LLM provider error", "details": exc.message},
        )

    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error"},
    )
