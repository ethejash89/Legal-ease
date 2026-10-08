from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class DocumentRequest(BaseModel):
    document_type: str = Field(..., min_length=2, max_length=120)
    parties: str = Field(..., min_length=2, max_length=5000)
    terms: str = Field(..., min_length=2, max_length=12000)
    effective_date: str = Field(..., min_length=2, max_length=80)
    jurisdiction: str = Field(default="India", min_length=2, max_length=120)
    additional_instructions: Optional[str] = Field(default="", max_length=5000)

    @field_validator("document_type", "parties", "terms", "effective_date", "jurisdiction")
    @classmethod
    def strip_required_strings(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value cannot be empty.")
        return value


class GenerateResponse(BaseModel):
    document_type: str
    content: str
    model: str
    mock: bool


class ExportRequest(BaseModel):
    document_type: str = Field(..., min_length=1, max_length=120)
    content: str = Field(..., min_length=1, max_length=1000000)
    parties: str = Field(default="", max_length=5000)
    effective_date: str = Field(default="", max_length=80)
