from abc import ABC, abstractmethod
from typing import TypeVar

T = TypeVar("T")


class LLMClient(ABC):
    @abstractmethod
    async def call(self, messages: list[dict], response_model: type[T]) -> T:
        ...

    @abstractmethod
    async def close(self):
        ...