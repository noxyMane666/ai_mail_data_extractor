from fastapi import Depends

from src.api.deps import get_llm_calling_service
from src.api.models import EmailExtractRequest, EmailExtractResponse
from src.services.llm_calling_service import LLMCallingService


def register_routes(app):
    @app.post("/api/v1/emails/extract-data")
    async def extract_data_from_text(
            request: EmailExtractRequest,
            llm_calling_service: LLMCallingService = Depends(get_llm_calling_service)
    ) -> EmailExtractResponse:
        return await llm_calling_service.extract_email_data(request.text)
