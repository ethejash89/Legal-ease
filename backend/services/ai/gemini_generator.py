import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

try:
    from google import genai
except ImportError:  # pragma: no cover
    genai = None


@dataclass
class GenerationResult:
    content: str
    model: str
    mock: bool


class GeminiDocumentGenerator:
    """Gemini-backed legal document generator with a deterministic local fallback."""

    def __init__(self) -> None:
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()
        self.mock_ai = os.getenv("MOCK_AI", "false").lower() in {"1", "true", "yes"}
        self.client = None

        if not self.mock_ai and self.api_key:
            if genai is None:
                raise RuntimeError(
                    "google-genai is not installed. Run: pip install -r requirements.txt"
                )
            self.client = genai.Client(api_key=self.api_key)

    @staticmethod
    def build_prompt(
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
        jurisdiction: str,
        additional_instructions: str = "",
    ) -> str:
        return f"""
You are a professional legal-document drafting assistant.

Create a structured DRAFT of a {document_type}.

Jurisdiction/context: {jurisdiction}
Effective date: {effective_date}
Parties: {parties}
User-specified terms:
{terms}

Additional instructions:
{additional_instructions or "None"}

Requirements:
- Produce only the document draft, not a conversational explanation.
- Use clear professional legal language.
- Do not invent names, dates, amounts, addresses, obligations, or facts that were not supplied.
- Where information is missing and materially necessary, use a bracketed placeholder such as [AMOUNT TO BE SPECIFIED].
- Include a clear title.
- Use numbered sections and useful subsections.
- Reflect every user-supplied term.
- Include signature blocks where appropriate.
- State that this is a draft and should be reviewed for the relevant jurisdiction when appropriate.
""".strip()

    def _mock_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
        jurisdiction: str,
    ) -> str:
        term_items = [x.strip() for x in terms.split(";") if x.strip()]
        terms_text = "\n".join(
            f"{i}. {item}" for i, item in enumerate(term_items, start=1)
        ) or "1. [TERMS TO BE SPECIFIED]"

        return f"""{document_type.upper()}

DRAFT LEGAL DOCUMENT

Effective Date: {effective_date}
Jurisdiction: {jurisdiction}

PARTIES
{parties}

1. PURPOSE
This draft {document_type} records the understanding between the parties identified above, based only on the information supplied by the user.

2. AGREED TERMS
{terms_text}

3. GENERAL PROVISIONS
The parties intend to comply with the obligations expressly stated in this draft. Any material information not supplied by the user should be completed before execution.

4. REVIEW
This is an AI-assisted draft prepared from user-provided information. It should be reviewed and adapted by a qualified legal professional for the applicable jurisdiction before signing.

SIGNATURES

____________________________
Party / Authorized Representative

Name: ______________________
Date: ______________________

____________________________
Party / Authorized Representative

Name: ______________________
Date: ______________________
"""

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
        jurisdiction: str,
        additional_instructions: str = "",
    ) -> GenerationResult:
        if self.mock_ai or not self.api_key:
            return GenerationResult(
                content=self._mock_document(
                    document_type, parties, terms, effective_date, jurisdiction
                ),
                model="mock",
                mock=True,
            )

        prompt = self.build_prompt(
            document_type,
            parties,
            terms,
            effective_date,
            jurisdiction,
            additional_instructions,
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            text = getattr(response, "text", None)
            if not text:
                raise RuntimeError("Gemini returned an empty response.")
            return GenerationResult(
                content=text.strip(),
                model=self.model_name,
                mock=False,
            )
        except Exception as exc:
            # Keep the local application usable if the remote provider fails.
            # The response clearly labels the result as mock content.
            fallback = self._mock_document(
                document_type, parties, terms, effective_date, jurisdiction
            )
            return GenerationResult(
                content=(
                    fallback
                    + f"\n\n[AI provider unavailable; local fallback used: {type(exc).__name__}]"
                ),
                model="mock-fallback",
                mock=True,
            )
