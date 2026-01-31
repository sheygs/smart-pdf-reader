import streamlit as st

from core.conversation import ConversationService
from core.pipeline import DocumentPipeline
from ui.session import SessionManager
from ui.html_templates import css, expander_css
from config import pdf_config, rate_limit_config
from ui.layout import AppLayout
from utils.file_handlers import FileHandler
from utils.pdf_renderer import PDFRenderer
from utils.rate_limiter import RateLimiter
from ui.components import ChatComponents, PDFComponents


def initialise_app():
    AppLayout.setup_page()
    st.markdown(css, unsafe_allow_html=True)
    SessionManager.initialize()


def handle_user_query(question: str):
    # Input validation
    if not question or not question.strip():
        return

    # Check rate limit
    is_allowed, error_message = RateLimiter.check_limit(SessionManager)
    if not is_allowed:
        st.warning(error_message)
        return

    # Record query for rate limiting
    RateLimiter.record_query(SessionManager)

    conversation = SessionManager.get("conversation")
    history = SessionManager.get("history", [])

    # Limit history length to prevent unbounded growth
    if len(history) > rate_limit_config.max_history_length:
        history = history[-rate_limit_config.max_history_length :]
        SessionManager.set("history", history)

    conversation_service = ConversationService()
    response = conversation_service.query(conversation, question, history)

    SessionManager.append_to_history(question, response["answer"])

    # safely extract page number from source documents
    if response.get("source_documents"):
        try:
            doc = response["source_documents"][0]
            page_num = doc.metadata.get("page", pdf_config.default_page)
            SessionManager.set("page_num", page_num)
        except (IndexError, KeyError, AttributeError):
            # Keep current page on error
            pass

    with SessionManager.get("expander"):
        ChatComponents.render_chat_history(SessionManager.get("history"))


def render_pdf_viewer():
    """
    Render PDF with answer page displayed prominently and context pages below
    """
    pdf_file = SessionManager.get("pdf_file")

    if not pdf_file:
        return

    try:
        temp_path = FileHandler.create_temp_file(pdf_file)
        current_page = SessionManager.get("page_num")

        images, start_page, end_page, total_pages, answer_page_index = (
            PDFRenderer.convert_pages_to_images(temp_path, current_page)
        )

        # render images with answer page first
        PDFComponents.render_pdf_images(
            images, answer_page_index, start_page, end_page, total_pages, current_page
        )

    except (FileNotFoundError, ValueError, OSError) as e:
        st.error(f"Error rendering PDF: {str(e)}")
        st.info("Try using the download button below to view the PDF locally")

        st.download_button(
            label="Download PDF",
            data=pdf_file.getvalue(),
            file_name="document.pdf",
            mime="application/pdf",
        )


def render_question_section():
    """Render the question form and chat expander."""
    AppLayout.render_header("Interactive Reader")

    is_document_processed = SessionManager.get("conversation") is not None
    with st.form(key="question_form", clear_on_submit=True):
        user_input = st.text_input(
            "Ask a question from the contents of the PDF:",
            disabled=not is_document_processed,
        )
        submit_question = st.form_submit_button(
            "Ask", disabled=not is_document_processed
        )

    # chat container
    expander = AppLayout.create_chat_expander()
    with expander:
        st.markdown(expander_css, unsafe_allow_html=True)

    return user_input, submit_question


def render_document_section():
    """Render document upload, validation, and processing."""
    AppLayout.render_header("Your Documents")
    pdf_file = st.file_uploader(
        "Upload a PDF here and click 'Process'", type=["pdf"]
    )

    # validate file size
    if (
        pdf_file
        and pdf_file.size > rate_limit_config.max_file_size_mb * 1024 * 1024
    ):
        st.error(
            f"File too large. Maximum size is {rate_limit_config.max_file_size_mb}MB"
        )
        pdf_file = None

    SessionManager.set("pdf_file", pdf_file)

    # check if a different file was uploaded
    current_file_name = pdf_file.name if pdf_file else None
    processed_file_name = SessionManager.get("processed_file_name")

    if (
        current_file_name
        and processed_file_name
        and current_file_name != processed_file_name
    ):
        SessionManager.set("conversation", None)
        SessionManager.set("processed_file_name", None)

    # disable Process button if this file is already processed
    is_already_processed = (
        SessionManager.get("conversation") is not None
        and current_file_name == processed_file_name
    )

    if st.button("Process", key="a", disabled=is_already_processed):
        with st.spinner("Processing..."):
            if pdf_file:
                chain = DocumentPipeline.process(pdf_file)
                if chain:
                    SessionManager.set("conversation", chain)
                    SessionManager.set("processed_file_name", pdf_file.name)
                    st.rerun()
                else:
                    st.error("Error processing PDF file")
            else:
                st.warning("Please provide a PDF file")


def render_results_section(submit_question: bool, user_input: str):
    """Handle query submission and render PDF viewer."""
    if submit_question:
        if user_input and user_input.strip():
            handle_user_query(user_input)
        else:
            st.warning("Please enter a question")

    render_pdf_viewer()


def main():
    initialise_app()
    column1, column2 = AppLayout.create_two_column_layout()

    with column1:
        user_input, submit_question = render_question_section()
        render_document_section()

    with column2:
        render_results_section(submit_question, user_input)


if __name__ == "__main__":
    main()
