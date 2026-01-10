from tempfile import NamedTemporaryFile

# import os

import streamlit as st
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings

# from langchain_community.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from pypdf import PdfReader
from pdf2image import convert_from_path

from html_templates import css, bot_template, user_template, expander_css

load_dotenv()

# openai_key = os.getenv("OPENAI_API_KEY")
# huggingface_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")


# T2: process user input
def process_file(document):
    # models available @ https://huggingface.co/spaces/mteb/leaderboard
    model_name = "thenlper/gte-small"
    model_kwargs = {"device": "cpu"}
    encode_kwargs = {"normalize_embeddings": False}

    embeddings = HuggingFaceEmbeddings(
        model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs
    )

    search_pdf = Chroma.from_documents(document, embeddings)

    chain = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(temperature=0.3),
        retriever=search_pdf.as_retriever(search_kwargs={"k": 2}),
        return_source_documents=True,
    )

    return chain


## T6: handle user input
def handle_input(query: str):
    response = st.session_state.conversation.invoke(
        {"question": query, "chat_history": st.session_state.history},
        return_only_outputs=True,
    )

    st.session_state.history += [(query, response["answer"])]

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
        page_title="Interactive PDF Reader", layout="wide", page_icon="📚"
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
                    # TODO: handle non-pdf docs
                    with NamedTemporaryFile(suffix=".pdf") as temp:
                        temp.write(st.session_state.pdf_file.getvalue())
                        temp.seek(0)
                        loader = PyPDFLoader(temp.name)
                        pdf = loader.load()
                        st.session_state.conversation = process_file(pdf)
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

                try:
                    # Convert PDF pages to images (works reliably on Streamlit Cloud)
                    current_page = st.session_state.page_num

                    # Calculate page range (current page ± 2 pages)
                    reader = PdfReader(temp.name)
                    total_pages = len(reader.pages)

                    start_page = max(current_page - 2, 0)
                    end_page = min(current_page + 2, total_pages - 1)

                    st.write(
                        f"Displaying pages {start_page + 1} to {end_page + 1} of {total_pages}"
                    )

                    # Convert PDF pages to images. first_page is 1-indexed for pdf2image
                    images = convert_from_path(
                        temp.name,
                        first_page=start_page + 1,
                        last_page=end_page + 1,
                        dpi=150,
                    )

                    # Display the answer page first (highlighted)
                    answer_page_index = current_page - start_page

                    if 0 <= answer_page_index < len(images):
                        st.markdown("### 📍 Answer found on this page:")
                        st.image(
                            images[answer_page_index],
                            caption=f"Page {current_page + 1} (Answer Source)",
                            width="stretch",
                        )

                    # Display other pages for context
                    if len(images) > 1:
                        st.markdown("### 📄 Context pages:")
                        for idx, image in enumerate(images):
                            if (
                                idx != answer_page_index
                            ):  # Skip the answer page we already showed
                                st.image(
                                    image,
                                    caption=f"Page {start_page + idx + 1}",
                                    width="stretch",
                                )

                except Exception as e:
                    st.error(f"Error displaying PDF: {str(e)}")
                    st.info(
                        "Try using the download button below to view the PDF locally"
                    )

                    # fallback: Provide download button
                    st.download_button(
                        label="Download PDF",
                        data=st.session_state.pdf_file.getvalue(),
                        file_name="document.pdf",
                        mime="application/pdf",
                    )


if __name__ == "__main__":
    main()
