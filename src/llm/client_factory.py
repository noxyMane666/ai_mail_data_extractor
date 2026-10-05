import logging

from src.config.app_settings import AppSettings
from src.llm.anthropic_client import AnthropicLLMClient
from src.llm.enums.client_types import LLMClientTypes
from src.llm.interfaces import LLMClient

logger = logging.getLogger(__name__)

ALLOWED_CLIENTS = {
    LLMClientTypes.anthropic: AnthropicLLMClient
}

async def create_llm_client(client_type: LLMClientTypes, config: AppSettings) -> LLMClient:
    chosen_client = ALLOWED_CLIENTS[client_type]
    logger.info(
        "LLM client created",
        extra={"event": "llm_client_created", "client_type": client_type.value},
    )
    return chosen_client(config)
