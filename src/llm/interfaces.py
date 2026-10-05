from abc import ABC, abstractmethod
from typing import TypeVar

from src.llm.llm_message import LLLMessage

T = TypeVar("T")


class LLMClient(ABC):
    @abstractmethod
    async def call(self, messages: list[LLLMessage], response_model: type[T] | None = None) -> T:
        ...

    @abstractmethod
    async def close(self):
        ...