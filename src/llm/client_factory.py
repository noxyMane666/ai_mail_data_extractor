from src.config.app_settings import AppSettings
from src.llm.anthropic_client import AnthropicLLMClient
from src.llm.enums.client_types import LLMClientTypes
from src.llm.interfaces import LLMClient


ALLOWED_CLIENTS = {
    LLMClientTypes.anthropic: AnthropicLLMClient
}

async def create_llm_client(client_type: LLMClientTypes, config: AppSettings) -> LLMClient:
    chosen_client = ALLOWED_CLIENTS[client_type]
    return chosen_client(config)