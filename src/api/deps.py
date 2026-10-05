from fastapi import Request

from src.llm.interfaces import LLMClient
from src.services.llm_calling_service import LLMCallingService


async def get_llm_client(request: Request) -> LLMClient:
    return request.app.state.llm_client

async def get_llm_calling_service(request: Request) -> LLMCallingService:
    client = await get_llm_client(request)
    return LLMCallingService(client)