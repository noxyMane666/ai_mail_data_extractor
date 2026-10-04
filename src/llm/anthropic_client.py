from typing import TypeVar

import httpx2
from anthropic import AsyncAnthropic
from anthropic.types import MessageParam

from src.config.app_settings import AppSettings
from src.llm.interfaces import LLMClient
from src.llm.llm_message import LLLMessage


T = TypeVar("T")


class AnthropicLLMClient(LLMClient):
    def __init__(self, config: AppSettings):
        self.client = AsyncAnthropic(
            api_key=config.anthropic_api_key,
            timeout=httpx2.Timeout(
                config.llm_default_timeout,
                read=config.llm_read_timeout,
                write=config.llm_write_timeout,
                connect=config.llm_connect_timeout,
            ),
        )
        self.model = config.anthropic_model_name
        self.max_tokens = config.llm_max_tokens

    async def call(
        self,
        messages: list[LLLMessage],
        response_model: type[T],
    ) -> T:
        typed_messages: list[MessageParam] = []

        for message in messages:
            typed_messages.append(
                {
                    "role": message.role.value,
                    "content": message.text,
                }
            )

        response = await self.client.messages.parse(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=typed_messages,
            output_format=response_model,
        )

        return response.parsed_output

    async def close(self) -> None:
        await self.client.close()