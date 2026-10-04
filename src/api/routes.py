from src.api.enums import UrgencyType
from src.api.models import EmailExtractRequest, EmailExtractResponse


def register_routes(app):
    @app.post("/api/v1/emails/extract-data")
    def extract_data_from_text(
            request: EmailExtractRequest
    ) -> EmailExtractResponse:
        return EmailExtractResponse(
            company_name="",
            contact_phone_number="",
            contact_email="",
            request_summary="",
            product_name="",
            urgency=UrgencyType.low
        )