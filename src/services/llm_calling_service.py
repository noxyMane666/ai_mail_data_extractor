from src.api.models import EmailExtractResponse
from src.llm.enums.message_roles import MessageRole
from src.llm.interfaces import LLMClient
from src.llm.llm_message import LLLMessage
from src.llm.prompts.prompts import EMAIL_DATA_EXTRACTION_BASE_PROMPT


class LLMCallingService:
    def __init__(self, llm_client: LLMClient):
        self._client = llm_client

    async def extract_email_data(self, email_text: str) -> EmailExtractResponse:
        system_message = LLLMessage(
            role=MessageRole.system,
            text=EMAIL_DATA_EXTRACTION_BASE_PROMPT
        )

        user_message = LLLMessage(
            role=MessageRole.user,
            text=email_text
        )

        return await self._client.call([system_message, user_message])