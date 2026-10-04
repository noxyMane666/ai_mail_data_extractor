from pydantic import BaseModel

from src.api.enums import UrgencyType


class EmailExtractRequest(BaseModel):
    text: str


class EmailExtractResponse(BaseModel):
    company_name: str | None
    contact_phone_number: str | None
    contact_email: str | None
    request_summary: str
    product_name: str | None
    urgency: UrgencyType