import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.routes import register_routes
from src.config.app_settings import AppSettings
from src.logging.logger_setup import setup_logging
from src.handlers.exception_handler import register_exception_handlers
from src.llm.client_factory import create_llm_client
from src.llm.enums.client_types import LLMClientTypes
from src.middleware.request_logging_middleware import register_logging_middleware

logger = logging.getLogger(__name__)


def create_app_lifespan(config: AppSettings):
    @asynccontextmanager
    async def app_lifespan(app: FastAPI):
        logger.info("Application starting", extra={"event": "app_starting"})
        try:
            llm_client = await create_llm_client(LLMClientTypes.anthropic, config)

            app.state.llm_client = llm_client
        except Exception as e:
            logger.exception("Failed to create LLM client", extra={"event": "llm_client_init_failed"})
            raise RuntimeError("Couldn't connect to llm client") from e

        logger.info("Application started", extra={"event": "app_started"})
        yield

        await app.state.llm_client.close()
        logger.info("Application stopped", extra={"event": "app_stopped"})

    return app_lifespan

def create_app() -> FastAPI:
    config = AppSettings()
    setup_logging(config.app_log_level)

    app = FastAPI(lifespan=create_app_lifespan(config))

    register_logging_middleware(app)
    register_routes(app)
    register_exception_handlers(app)
    return app
