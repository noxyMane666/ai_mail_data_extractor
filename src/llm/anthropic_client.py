import logging
import time
from typing import TypeVar

import httpx2
from anthropic import NOT_GIVEN, AsyncAnthropic
from anthropic.types import MessageParam

from src.config.app_settings import AppSettings
from src.llm.enums.message_roles import MessageRole
from src.llm.interfaces import LLMClient
from src.llm.llm_message import LLLMessage


T = TypeVar("T")

logger = logging.getLogger(__name__)


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
        response_model: type[T] | None = None
    ) -> T:
        system_parts: list[str] = []
        typed_messages: list[MessageParam] = []

        for message in messages:
            if message.role == MessageRole.system:
                system_parts.append(message.text)
            else:
                typed_messages.append(
                    {
                        "role": message.role.value,
                        "content": message.text,
                    }
                )

        logger.info(
            "LLM request started",
            extra={
                "event": "llm_request_started",
                "model": self.model,
                "messages_count": len(typed_messages),
                "input_chars": sum(len(message.text) for message in messages),
            },
        )

        start_time = time.perf_counter()
        response = await self.client.messages.parse(
            model=self.model,
            max_tokens=self.max_tokens,
            system="\n\n".join(system_parts) or NOT_GIVEN,
            messages=typed_messages,
            output_format=response_model or NOT_GIVEN,
        )
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        logger.info(
            "LLM request completed",
            extra={
                "event": "llm_request_completed",
                "duration_ms": duration_ms,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "stop_reason": response.stop_reason,
            },
        )

        if response.parsed_output is None:
            logger.error(
                "LLM response could not be parsed",
                extra={"event": "llm_response_not_parsed", "stop_reason": response.stop_reason},
            )
            raise ValueError("LLM response could not be parsed into the requested model")

        return response.parsed_output

    async def close(self) -> None:
        await self.client.close()