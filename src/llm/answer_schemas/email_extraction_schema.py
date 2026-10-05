from pydantic import BaseModel, Field

from src.api.enums.urgency_types import UrgencyType


class ExtractedEmailData(BaseModel):
    company_name: str | None = Field(
        description="Название компании отправителя с организационно-правовой формой, либо null.",
    )
    contact_phone_number: str | None = Field(
        description="Телефон контакта отправителя. Российский номер в виде +7XXXXXXXXXX, либо null.",
    )
    contact_email: str | None = Field(
        description="Email отправителя или контактного лица из письма, либо null.",
    )
    request_summary: str = Field(
        description="Суть запроса в одном-двух предложениях на русском языке.",
    )
    product_name: str | None = Field(
        description="Название товара или услуги, к которой относится запрос, либо null.",
    )
    urgency: UrgencyType = Field(
        description="Срочность запроса: high, medium или low.",
    )
