from dataclasses import dataclass

from src.llm.enums.message_roles import MessageRole


@dataclass
class LLLMessage:
    role: MessageRole
    text: str
