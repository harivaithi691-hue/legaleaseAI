import html
import os
import sys
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv


# ------------------------------------------
# Project path configuration
# ------------------------------------------

ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


load_dotenv(ROOT_DIR / ".env")


from shared.exporters import (
    format_docx,
    format_pdf,
    format_txt
)


# ------------------------------------------
# Configuration
# ------------------------------------------

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://localhost:8000"
)


# ------------------------------------------
# Page configuration
# ------------------------------------------

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ------------------------------------------
# Custom CSS
# ------------------------------------------

st.markdown(
    """
<style>

.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    color: #777;
    font-size: 17px;
    margin-bottom: 30px;
}

.preview-card {
    background-color: #111827;
    color: #f9fafb;
    padding: 30px;
    border-radius: 15px;
    border: 1px solid #374151;
    max-height: 650px;
    overflow-y: auto;
    white-space: pre-wrap;
    font-family: Georgia, serif;
    line-height: 1.7;
}

.info-box {
    padding: 15px;
    border-radius: 10px;
    background-color: #f3f4f6;
    margin-bottom: 20px;
}

.footer {
    text-align: center;
    color: #888;
    padding: 30px;
}

</style>
""",
    unsafe_allow_html=True
)


# ------------------------------------------
# Header
# ------------------------------------------

st.markdown(
    '<div class="main-title">⚖️ LegalEase</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
<div class="subtitle">
AI-Powered Legal Document Generator
</div>
""",
    unsafe_allow_html=True
)


st.markdown(
    """
<div class="info-box">
<b>LegalEase</b> helps generate editable drafts of common
legal documents using AI. Always review generated documents
carefully and obtain professional legal advice when appropriate.
</div>
""",
    unsafe_allow_html=True
)


# ------------------------------------------
# Session state
# ------------------------------------------

if "generated_document" not in st.session_state:
    st.session_state.generated_document = ""

if "document_type" not in st.session_state:
    st.session_state.document_type = "Freelance Work Contract"


# ------------------------------------------
# Sidebar
# ------------------------------------------

with st.sidebar:

    st.header("⚙️ Settings")

    backend_url = st.text_input(
        "Backend URL",
        value=BACKEND_URL
    )

    st.caption(
        "FastAPI backend used for AI generation."
    )

    if st.button("🔍 Check Backend"):

        try:

            response = requests.get(
                f"{backend_url}/health",
                timeout=5
            )

            if response.ok:

                st.success(
                    "Backend is running."
                )

                st.json(
                    response.json()
                )

            else:

                st.error(
                    f"Backend returned {response.status_code}"
                )

        except requests.RequestException as exc:

            st.error(
                f"Could not connect: {exc}"
            )


# ------------------------------------------
# Main input area
# ------------------------------------------

left, right = st.columns(
    [1, 1],
    gap="large"
)


with left:

    st.subheader(
        "📄 Document Information"
    )

    document_type = st.selectbox(
        "Document Type",
        [
            "Freelance Work Contract",
            "Non-Disclosure Agreement",
            "Lease Agreement",
            "Employment Contract",
            "Employment Offer Letter",
            "Service Agreement",
            "Consulting Agreement",
            "Partnership Agreement",
            "General Agreement",
            "Other"
        ]
    )

    if document_type == "Other":

        document_type = st.text_input(
            "Specify document type"
        )

    parties = st.text_area(
        "Parties Involved",
        placeholder=(
            "Example:\n"
            "Jane Doe (Service Provider)\n"
            "TechNova Inc. (Client)"
        ),
        height=140
    )

    terms = st.text_area(
        "Terms & Conditions",
        placeholder=(
            "Enter each term separated by a semicolon.\n\n"
            "Payment must be made within 30 days;\n"
            "Provider must deliver the work by the deadline;\n"
            "Confidential information must remain confidential;\n"
            "Either party may terminate with 15 days notice"
        ),
        height=220
    )

    effective_date = st.text_input(
        "Effective Date",
        placeholder="Example: April 15, 2026"
    )

    additional_instructions = st.text_area(
        "Additional Instructions (Optional)",
        placeholder=(
            "Example: Use simple language and include "
            "a strong confidentiality clause."
        ),
        height=120
    )

    logo_file = st.file_uploader(
        "Company Logo (Optional)",
        type=[
            "png",
            "jpg",
            "jpeg"
        ]
    )

    generate = st.button(
        "🚀 Generate Document",
        type="primary",
        use_container_width=True
    )


# ------------------------------------------
# Generation
# ------------------------------------------

if generate:

    if not document_type.strip():
        st.error(
            "Please enter a document type."
        )

    elif not parties.strip():
        st.error(
            "Please enter the parties."
        )

    elif not terms.strip():
        st.error(
            "Please enter the terms."
        )

    elif not effective_date.strip():
        st.error(
            "Please enter the effective date."
        )

    else:

        payload = {
            "document_type": document_type,
            "parties": parties,
            "terms": terms,
            "effective_date": effective_date,
            "additional_instructions": (
                additional_instructions
            )
        }

        with st.spinner(
            "Generating legal document..."
        ):

            try:

                response = requests.post(
                    f"{backend_url}/api/generate",
                    json=payload,
                    timeout=120
                )

                if response.ok:

                    data = response.json()

                    st.session_state.generated_document = (
                        data["content"]
                    )

                    st.success(
                        "Document generated successfully."
                    )

                else:

                    try:
                        detail = response.json().get(
                            "detail",
                            response.text
                        )
                    except Exception:
                        detail = response.text

                    st.error(
                        f"Generation failed: {detail}"
                    )

            except requests.RequestException as exc:

                st.error(
                    "Could not connect to the FastAPI "
                    f"backend.\n\n{exc}"
                )


# ------------------------------------------
# Output area
# ------------------------------------------

with right:

    st.subheader(
        "👁️ Document Preview"
    )

    document = st.session_state.generated_document

    if document:

        preview_html = html.escape(
            document
        )

        st.markdown(
            f"""
<div class="preview-card">
{preview_html}
</div>
""",
            unsafe_allow_html=True
        )

        st.divider()

        st.subheader(
            "✏️ Edit Document"
        )

        edited_document = st.text_area(
            "Modify the generated document",
            value=document,
            height=500,
            label_visibility="collapsed"
        )

        st.session_state.generated_document = (
            edited_document
        )

        st.divider()

        st.subheader(
            "⬇️ Download"
        )

        logo_path = None

        temporary_logo = None

        if logo_file:

            import tempfile

            suffix = Path(
                logo_file.name
            ).suffix

            temporary_logo = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix
            )

            temporary_logo.write(
                logo_file.getvalue()
            )

            temporary_logo.close()

            logo_path = temporary_logo.name

        txt_data = format_txt(
            edited_document
        )

        docx_data = format_docx(
            edited_document,
            document_type,
            logo_path
        )

        pdf_data = format_pdf(
            edited_document,
            document_type,
            logo_path
        )

        download_col1, download_col2, download_col3 = (
            st.columns(3)
        )

        with download_col1:

            st.download_button(
                label="📄 Download TXT",
                data=txt_data,
                file_name=(
                    "legalease_document.txt"
                ),
                mime="text/plain",
                use_container_width=True
            )

        with download_col2:

            st.download_button(
                label="📝 Download DOCX",
                data=docx_data,
                file_name=(
                    "legalease_document.docx"
                ),
                mime=(
                    "application/vnd.openxmlformats-"
                    "officedocument.wordprocessingml.document"
                ),
                use_container_width=True
            )

        with download_col3:

            st.download_button(
                label="📕 Download PDF",
                data=pdf_data,
                file_name=(
                    "legalease_document.pdf"
                ),
                mime="application/pdf",
                use_container_width=True
            )

        if temporary_logo:

            try:
                os.unlink(
                    temporary_logo.name
                )
            except OSError:
                pass

    else:

        st.info(
            "Your generated document will appear here."
        )


# ------------------------------------------
# Footer
# ------------------------------------------

st.markdown(
    """
<div class="footer">
LegalEase • AI-Powered Legal Document Generator
<br>
AI-generated documents should be reviewed before use.
</div>
""",
    unsafe_allow_html=True
)