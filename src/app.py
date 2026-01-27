import streamlit as st

from core.document_processor import DocumentProcessor
from core.embeddings import EmbeddingService
from core.vector_store import VectorStore
from core.conversation import ConversationService
from ui.session import SessionManager
from ui.html_templates import css, expander_css
from config import model_config, api_config
from ui.layout import AppLayout
from utils.file_handlers import FileHandler
from utils.pdf_renderer import PDFRenderer
from ui.components import ChatComponents, PDFComponents


def initialise_app():
    """Initialize app configuration and session"""
    api_config.validate()
    AppLayout.setup_page()
    st.markdown(css, unsafe_allow_html=True)
    SessionManager.initialize()


def process_uploaded_file(uploaded_file):

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


## handle user input
def handle_user_query(question: str):
    conversation = SessionManager.get("conversation")
    history = SessionManager.get("history")

    # response
    response = ConversationService().query(conversation.invoke, question, history)

    # update history
    SessionManager.append_to_history(question, response["answer"])

    # update page num
    if response.get("source_documents"):
        page_num = list(response["source_documents"][0])[1][1]["page"]
        SessionManager.set("page_num", page_num)

    # Render chat
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

        # Convert PDF pages to images
        images, start_page, end_page, total_pages, answer_page_index = (
            PDFRenderer.convert_pages_to_images(temp_path, current_page)
        )

        # Render images with answer page first
        PDFComponents.render_pdf_images(
            images, answer_page_index, start_page, end_page, total_pages, current_page
        )

    except Exception as e:
        st.error(f"Error rendering PDF: {str(e)}")
        st.info("Try using the download button below to view the PDF locally")

        # Fallback: Provide download button
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
        AppLayout.render_header("Interactive Reader 📚")

        user_input = st.text_input("Ask a question from the contents of the PDF:")
        SessionManager.set("user_input", user_input)

        st.write(SessionManager.get("user_input"))

        # chat container
        expander = AppLayout.create_chat_expander()
        with expander:
            st.markdown(expander_css, unsafe_allow_html=True)

        ## pdf upload
        AppLayout.render_header("Your Documents")
        pdf_file = st.file_uploader("Upload a PDF here and click ‘Process’")
        SessionManager.set("pdf_file", pdf_file)

        st.write(SessionManager.get("pdf_file"))

        if st.button("Process", key="a"):
            with st.spinner("Processing..."):
                if pdf_file:
                    chain = process_uploaded_file(pdf_file)
                    if chain:
                        SessionManager.set("conversation", chain)
                        st.markdown("Done processing. You may now ask a question.")
                    else:
                        st.error("Error processing PDF file")

                else:
                    st.write("Please provide a PDF file")

    ## handle query and display pages
    with column2:
        user_input = SessionManager.get("user_input")
        conversation = SessionManager.get("conversation")

        if user_input and conversation:
            handle_user_query(user_input)
        elif user_input:
            st.warning("Please upload and process a PDF first")

        render_pdf_viewer()


if __name__ == "__main__":
    main()
