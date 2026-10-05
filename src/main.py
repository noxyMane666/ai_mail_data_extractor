from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.routes import register_routes
from src.config.app_settings import AppSettings
from src.handlers.exception_handler import register_exception_handlers
from src.llm.client_factory import create_llm_client
from src.llm.enums.client_types import LLMClientTypes


def create_app_lifespan(config: AppSettings):
    @asynccontextmanager
    async def app_lifespan(app: FastAPI):
        try:
            llm_client = await create_llm_client(LLMClientTypes.anthropic, config)

            app.state.llm_client = llm_client
        except Exception as e:
            raise RuntimeError("Couldn't connect to llm client") from e

        yield

        await app.state.llm_client.close()

    return app_lifespan

def create_app() -> FastAPI:
    config = AppSettings()
    app = FastAPI(lifespan=create_app_lifespan(config))

    register_routes(app)
    register_exception_handlers(app)
    return app