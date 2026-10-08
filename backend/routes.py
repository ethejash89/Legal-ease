from fastapi import APIRouter
from fastapi.responses import Response

from .schemas import DocumentRequest, ExportRequest, GenerateResponse
from .services.ai.gemini_generator import GeminiDocumentGenerator
from .services.document_service import format_html_preview
from .services.export_service import export_docx, export_pdf, export_txt

router = APIRouter()
generator = GeminiDocumentGenerator()


@router.post("/generate", response_model=GenerateResponse)
def generate_document(request: DocumentRequest) -> GenerateResponse:
    result = generator.generate_document(
        document_type=request.document_type,
        parties=request.parties,
        terms=request.terms,
        effective_date=request.effective_date,
        jurisdiction=request.jurisdiction,
        additional_instructions=request.additional_instructions or "",
    )
    return GenerateResponse(
        document_type=request.document_type,
        content=result.content,
        model=result.model,
        mock=result.mock,
    )


@router.post("/preview")
def preview_document(request: ExportRequest) -> dict:
    return {"html": format_html_preview(request.content)}


@router.post("/export/txt")
def download_txt(request: ExportRequest) -> Response:
    filename = "legal_document.txt"
    return Response(
        content=export_txt(request.content),
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/export/docx")
def download_docx(request: ExportRequest) -> Response:
    filename = "legal_document.docx"
    data = export_docx(
        request.content,
        request.document_type,
        request.parties,
        request.effective_date,
    )
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/export/pdf")
def download_pdf(request: ExportRequest) -> Response:
    filename = "legal_document.pdf"
    data = export_pdf(request.content, request.document_type)
    return Response(
        content=data,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
