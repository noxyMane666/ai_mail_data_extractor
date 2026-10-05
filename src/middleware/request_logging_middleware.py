import logging
import re
import time
import uuid

from fastapi import FastAPI, Request

from src.logging.logging_context import RequestContext

logger = logging.getLogger(__name__)

VALID_REQUEST_ID = re.compile(r"^[A-Za-z0-9-]{1,64}$")


def _resolve_request_id(request: Request) -> str:
    incoming = request.headers.get("x-request-id", "")
    return incoming if VALID_REQUEST_ID.fullmatch(incoming) else str(uuid.uuid4())


def register_logging_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def request_logging_middleware(request: Request, call_next):
        request_id = _resolve_request_id(request)
        request.state.request_id = request_id

        start_time = time.perf_counter()
        response = None
        with RequestContext.bind(request_id, request.method, request.url.path):
            try:
                response = await call_next(request)
                return response
            finally:
                duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
                status_code = response.status_code if response is not None else 500
                logger.info(
                    "Request completed",
                    extra={
                        "event": "request_completed",
                        "status_code": status_code,
                        "duration_ms": duration_ms,
                    },
                )
                if response is not None:
                    response.headers["x-request-id"] = request_id
