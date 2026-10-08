import os
from datetime import date

import requests
import streamlit as st
from dotenv import load_dotenv

from backend.services.document_service import format_html_preview

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container { max-width: 1200px; padding-top: 2rem; }
    .legal-card {
        background: #111827;
        border: 1px solid #374151;
        border-radius: 14px;
        padding: 24px;
        color: #f9fafb;
        max-height: 620px;
        overflow-y: auto;
        line-height: 1.65;
    }
    .legal-card h2, .legal-card h3 { color: #ffffff; }
    .legal-card p { color: #e5e7eb; }
    .muted { color: #6b7280; }
    </style>
    """,
    unsafe_allow_html=True,
)

with open("assets/legal_ease_logo.svg", "r", encoding="utf-8") as f:
    logo_svg = f.read()

st.markdown(f"<div style='text-align:center'>{logo_svg}</div>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center'>LegalEase</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;color:#6b7280'>AI-powered legal document drafting and export</p>",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Document details")
    document_type = st.selectbox(
        "Document type",
        [
            "Employment Contract",
            "Non-Disclosure Agreement",
            "Lease Agreement",
            "Employment Offer Letter",
            "Freelance Work Contract",
            "Service Agreement",
            "General Agreement",
        ],
    )
    custom_type = st.text_input("Or enter a custom type")
    if custom_type.strip():
        document_type = custom_type.strip()

    parties = st.text_area(
        "Parties involved",
        placeholder="Jane Doe (Service Provider), TechNova Inc. (Client)",
        height=100,
    )

    terms = st.text_area(
        "Terms & conditions",
        placeholder=(
            "Payment to be made within 30 days of invoice; "
            "Confidentiality must be maintained; "
            "Either party may terminate with 15 days notice"
        ),
        height=180,
        help="Separate individual terms with semicolons.",
    )

    effective_date = st.date_input("Effective date", value=date.today())
    jurisdiction = st.text_input("Jurisdiction", value="India")
    additional = st.text_area(
        "Additional instructions",
        placeholder="Use concise professional language and include signature blocks.",
        height=100,
    )

    generate = st.button("Generate Document", type="primary", use_container_width=True)

if "content" not in st.session_state:
    st.session_state.content = ""
if "document_type" not in st.session_state:
    st.session_state.document_type = document_type

if generate:
    if not parties.strip() or not terms.strip():
        st.error("Please provide parties and terms before generating.")
    else:
        payload = {
            "document_type": document_type,
            "parties": parties,
            "terms": terms,
            "effective_date": effective_date.isoformat(),
            "jurisdiction": jurisdiction,
            "additional_instructions": additional,
        }
        try:
            with st.spinner("Generating your draft..."):
                response = requests.post(
                    f"{BACKEND_URL}/generate",
                    json=payload,
                    timeout=120,
                )
            response.raise_for_status()
            data = response.json()
            st.session_state.content = data["content"]
            st.session_state.document_type = data["document_type"]
            st.session_state.parties = parties
            st.session_state.effective_date = effective_date.isoformat()
            if data.get("mock"):
                st.info("Local/mock generation was used. Configure GEMINI_API_KEY and MOCK_AI=false for live Gemini.")
            else:
                st.success(f"Generated with {data.get('model', 'Gemini')}.")
        except requests.RequestException as exc:
            st.error(
                "Could not reach the FastAPI backend. Start it with "
                "`python -m uvicorn backend.main:app --reload`."
            )
            st.exception(exc)

if st.session_state.content:
    st.subheader("Document workspace")

    left, right = st.columns([1, 1])

    with left:
        st.markdown("### Editable document")
        edited = st.text_area(
            "Edit generated content",
            value=st.session_state.content,
            height=600,
            label_visibility="collapsed",
        )
        st.session_state.content = edited

    with right:
        st.markdown("### Preview")
        preview_html = format_html_preview(st.session_state.content)
        st.markdown(
            f"<div class='legal-card'>{preview_html}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("### Download")
    export_payload = {
        "document_type": st.session_state.document_type,
        "content": st.session_state.content,
        "parties": st.session_state.get("parties", ""),
        "effective_date": st.session_state.get("effective_date", ""),
    }

    c1, c2, c3 = st.columns(3)

    def get_export(path: str):
        response = requests.post(
            f"{BACKEND_URL}{path}",
            json=export_payload,
            timeout=60,
        )
        response.raise_for_status()
        return response.content

    with c1:
        try:
            txt = get_export("/export/txt")
            st.download_button(
                "Download TXT",
                data=txt,
                file_name="legal_document.txt",
                mime="text/plain",
                use_container_width=True,
            )
        except requests.RequestException:
            st.warning("TXT export unavailable.")

    with c2:
        try:
            docx = get_export("/export/docx")
            st.download_button(
                "Download DOCX",
                data=docx,
                file_name="legal_document.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        except requests.RequestException:
            st.warning("DOCX export unavailable.")

    with c3:
        try:
            pdf = get_export("/export/pdf")
            st.download_button(
                "Download PDF",
                data=pdf,
                file_name="legal_document.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except requests.RequestException:
            st.warning("PDF export unavailable.")

st.divider()
st.caption(
    "LegalEase creates AI-assisted drafts. It does not replace advice from a qualified legal professional."
)
