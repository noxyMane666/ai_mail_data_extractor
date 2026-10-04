from fastapi import Request

from src.llm.interfaces import LLMClient


async def get_llm_client(request: Request) -> LLMClient:
    return request.app.state.llm_client