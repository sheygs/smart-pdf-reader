from tempfile import NamedTemporaryFile
import base64

import streamlit as st

# from langchain_huggingface import HuggingFaceEmbeddings

# from langchain_community.embeddings import OpenAIEmbeddings
# from langchain_openai import ChatOpenAI
# from langchain.chains import ConversationalRetrievalChain
# from langchain_community.vectorstores import Chroma

# from langchain_community.document_loaders import PyPDFLoader
from pypdf import PdfReader, PdfWriter

from html_templates import css, bot_template, user_template, expander_css
from config import model_config, api_config, ui_config, pdf_config
from core.document_processor import DocumentProcessor
from core.embeddings import EmbeddingService
from core.vector_store import VectorStore
from core.conversation import ConversationService


# T2: process user input
def process_file(document):
    # models available @ https://huggingface.co/spaces/mteb/leaderboard

    # model_name = model_config.embedding_model
    # model_kwargs = {"device": model_config.embedding_device}
    # encode_kwargs = {"normalize_embeddings": model_config.normalize_embeddings}

    api_config.validate()

    # embeddings = HuggingFaceEmbeddings(
    #     model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs
    # )

    embedding_service = EmbeddingService()
    embeddings = embedding_service.get_embeddings()

    # search_pdf = Chroma.from_documents(document, embeddings)

    vector_store = VectorStore(embeddings)
    vector_store.create_from_store(document)
    retriever = vector_store.as_retriever(model_config.retrieval_k)

    # chain = ConversationalRetrievalChain.from_llm(
    #     # ChatOpenAI automatically picks up the API keys from environment variables
    #     # however, you can explicitly add it there to utilise the APIConfig
    #     llm=ChatOpenAI(
    #         temperature=model_config.llm_temperature, api_key=api_config.openai_api_key
    #     ),
    #     # retriever=search_pdf.as_retriever(
    #     #     search_kwargs={"k": model_config.retrieval_k}
    #     # ),
    #     retriever=retriever,
    #     return_source_documents=True,
    # )

    # return chain
    conversation_service = ConversationService()
    chain = conversation_service.create_chain(retriever)
    return chain


## T6: handle user input
def handle_input(question: str):
    response = ConversationService().query(
        st.session_state.conversation.invoke, question, st.session_state.history
    )
    # response = st.session_state.conversation.invoke(
    #     {"question": question, "chat_history": st.session_state.history},
    #     return_only_outputs=True,
    # )

    st.session_state.history += [(question, response["answer"])]

    st.session_state.page_num = list(response["source_documents"][0])[1][1]["page"]

    for _, message in enumerate(st.session_state.history):
        st.session_state.expander.write(
            user_template.replace("{{MSG}}", message[0]), unsafe_allow_html=True
        )
        st.session_state.expander.write(
            bot_template.replace("{{MSG}}", message[1]), unsafe_allow_html=True
        )


def main():
    ## T3: create Web-page Layout

    st.set_page_config(
        page_title=ui_config.page_title,
        layout=ui_config.page_layout,
        page_icon=ui_config.page_icon,
    )

    st.markdown(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None

    if "history" not in st.session_state:
        st.session_state.history = []

    if "page_num" not in st.session_state:
        st.session_state.page_num = 0

    # column1, column2 = st.columns([1, 1])
    column1, column2 = st.columns(2)

    with column1:
        st.header("Interactive Reader 📚")

        user_input = st.text_input("Ask a question from the contents of the PDF:")

        st.session_state.user_input = user_input

        # st.write(st.session_state.user_input)  # logging

        st.session_state.expander = st.expander("Your Chat History", expanded=True)

        with st.session_state.expander:
            st.markdown(expander_css, unsafe_allow_html=True)

        ## T5: load and process the PDF
        st.header("Your Documents")

        st.session_state.pdf_file = st.file_uploader(
            "Upload a PDF here and click ‘Process’"
        )

        # st.write(st.session_state.pdf_file)

        if st.button("Process", key="a"):
            with st.spinner("Processing..."):
                if st.session_state.pdf_file is not None:
                    with NamedTemporaryFile(suffix=".pdf") as temp:
                        temp.write(st.session_state.pdf_file.getvalue())
                        temp.seek(0)
                        st.write(temp.name)
                        # loader = PyPDFLoader(temp.name)
                        # pdf = loader.load()

                        pdf_docs = DocumentProcessor.load_pdf(temp.name)

                        print({"pdf": pdf_docs})
                        st.session_state.conversation = process_file(pdf_docs)
                        st.markdown("Done processing. You may now ask a question.")

                else:
                    st.write("Please provide a PDF file")

    ## T7: handle query & display pages
    with column2:
        if st.session_state.user_input and st.session_state.conversation:
            handle_input(st.session_state.user_input)
        elif st.session_state.user_input:
            st.warning("Please upload and process a PDF first")

        if st.session_state.get("pdf_file"):
            with NamedTemporaryFile(suffix=".pdf", delete=False) as temp:
                temp.write(st.session_state.pdf_file.getvalue())
                temp.seek(0)
                reader = PdfReader(temp.name)

                pdf_writer = PdfWriter()

                current_page = st.session_state.page_num

                start = max(current_page - pdf_config.context_page_before, 0)
                end = min(
                    current_page + pdf_config.context_page_after, len(reader.pages) - 1
                )

                while start <= end:
                    pdf_writer.add_page(reader.pages[start])
                    start += 1

                with NamedTemporaryFile(suffix=".pdf", delete=False) as temp1:
                    pdf_writer.write(temp1.name)
                    with open(temp1.name, "rb") as f:
                        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
                        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}#page=1" width="100%" height="900" type="application/pdf" frameborder="0"></iframe>'
                        st.markdown(pdf_display, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
