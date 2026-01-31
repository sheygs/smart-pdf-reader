import time

import streamlit as st

from core.document_processor import DocumentProcessor
from core.embeddings import EmbeddingService
from core.vector_store import VectorStore
from core.conversation import ConversationService
from ui.session import SessionManager
from ui.html_templates import css, expander_css
from config import model_config, pdf_config, rate_limit_config
from ui.layout import AppLayout
from utils.file_handlers import FileHandler
from utils.pdf_renderer import PDFRenderer
from ui.components import ChatComponents, PDFComponents


def initialise_app():
    AppLayout.setup_page()
    st.markdown(css, unsafe_allow_html=True)
    SessionManager.initialize()


def process_uploaded_file(uploaded_file):
    # Clean up previous temp files before creating new ones
    FileHandler.cleanup_temp_files()

    temp_path = FileHandler.create_temp_file(uploaded_file)

    documents = DocumentProcessor.load_pdf(temp_path)

    embedding_service = EmbeddingService()
    embeddings = embedding_service.get_embeddings()

    vector_store = VectorStore(embeddings)
    vector_store.create_from_store(documents)
    retriever = vector_store.as_retriever(model_config.retrieval_k)

    conversation_service = ConversationService()
    chain = conversation_service.create_chain(retriever)
    return chain


def check_rate_limit() -> bool:
    """Check if user has exceeded rate limits."""
    query_count = SessionManager.get("query_count") or 0
    last_query_time = SessionManager.get("last_query_time") or 0.0

    # Cooldown check
    if time.time() - last_query_time < rate_limit_config.cooldown_seconds:
        st.warning("Please wait before sending another query.")
        return False

    # Max queries check
    if query_count >= rate_limit_config.max_queries_per_session:
        st.error("Session query limit reached. Please refresh the page.")
        return False

    return True


def handle_user_query(question: str):
    # Input validation
    if not question or not question.strip():
        return

    if not check_rate_limit():
        return

    # Update rate limit counters
    SessionManager.set("query_count", (SessionManager.get("query_count") or 0) + 1)
    SessionManager.set("last_query_time", time.time())

    conversation = SessionManager.get("conversation")
    history = SessionManager.get("history") or []

    # Limit history length to prevent unbounded growth
    if len(history) > rate_limit_config.max_history_length:
        history = history[-rate_limit_config.max_history_length:]
        SessionManager.set("history", history)

    conversation_service = ConversationService()
    response = conversation_service.query(conversation, question, history)

    SessionManager.append_to_history(question, response["answer"])

    # Safely extract page number from source documents
    if response.get("source_documents"):
        try:
            doc = response["source_documents"][0]
            page_num = doc.metadata.get("page", pdf_config.default_page)
            SessionManager.set("page_num", page_num)
        except (IndexError, KeyError, AttributeError):
            pass  # Keep current page on error

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


def main():
    initialise_app()

    column1, column2 = AppLayout.create_two_column_layout()

    with column1:
        AppLayout.render_header("Interactive Reader")

        user_input = st.text_input("Ask a question from the contents of the PDF:")
        SessionManager.set("user_input", user_input)

        # chat container
        expander = AppLayout.create_chat_expander()
        with expander:
            st.markdown(expander_css, unsafe_allow_html=True)

        ## pdf upload
        AppLayout.render_header("Your Documents")
        pdf_file = st.file_uploader(
            "Upload a PDF here and click 'Process'",
            type=["pdf"]
        )

        # Validate file size
        if pdf_file and pdf_file.size > rate_limit_config.max_file_size_mb * 1024 * 1024:
            st.error(f"File too large. Maximum size is {rate_limit_config.max_file_size_mb}MB")
            pdf_file = None

        SessionManager.set("pdf_file", pdf_file)

        if st.button("Process", key="a"):
            with st.spinner("Processing..."):
                if pdf_file:
                    chain = process_uploaded_file(pdf_file)
                    if chain:
                        SessionManager.set("conversation", chain)
                        st.success("Done processing. You may now ask a question.")
                    else:
                        st.error("Error processing PDF file")
                else:
                    st.warning("Please provide a PDF file")

    with column2:
        user_input = SessionManager.get("user_input")
        conversation = SessionManager.get("conversation")

        if user_input and user_input.strip() and conversation:
            handle_user_query(user_input)
        elif user_input and user_input.strip():
            st.warning("Please upload and process a PDF first")

        render_pdf_viewer()


if __name__ == "__main__":
    main()
