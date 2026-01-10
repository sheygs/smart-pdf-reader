from tempfile import NamedTemporaryFile
import base64
import os

import streamlit as st
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from pypdf import PdfReader, PdfWriter


from html_templates import css, bot_template, user_template, expander_css

load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
huggingface_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")


# T2: process user input
def process_file(document):
    # available models here: https://huggingface.co/spaces/mteb/leaderboard
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


## T6: Method for Handling User Input
def handle_input(query):
    response = st.session_state.conversation(
        {"question": query, "chat_history": st.session_state.history},
        return_only_outputs=True,
    )

    st.session_state.history += [(query, response["answer"])]

    st.session_state.page_number = list(response["source_documents"][0])[1][1]["page"]

    for _, message in enumerate(st.session_state.history):
        st.session_state.expander.write(
            user_template.replace("{{MSG}}", message[0]), unsafe_allow_html=True
        )
        st.session_state.expander.write(
            bot_template.replace("{{MSG}}", message[1]), unsafe_allow_html=True
        )


def main():
    ## T3: Create Web-page Layout
    st.set_page_config(
        page_title="Interactive PDF Reader", layout="wide", page_icon="📕"
    )

    st.markdown(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None

    if "history" not in st.session_state:
        st.session_state.history = []

    if "page_num" not in st.session_state:
        st.session_state.page_num = 0

    column1, column2 = st.columns([1, 1])
    # column1, column2 = st.columns(2)

    with column1:
        st.header("Interactive Reader 📕")

        user_input = st.text_input("Ask a question from the contents of the PDF:")

        st.session_state.user_input = user_input

        st.write(st.session_state.user_input)

        st.session_state.expander = st.expander("Your Chat", expanded=True)

        with st.session_state.expander:
            st.markdown(expander_css, unsafe_allow_html=True)

        ## T5: Load and Process the PDF
        st.header("Your Documents")

        st.session_state.pdf_file = st.file_uploader(
            "Upload a PDF here and click ‘Process’"
        )

        st.write(st.session_state.pdf_file)

        if st.button("Process", key="b"):
            with st.spinner("Processing..."):
                if st.session_state.pdf_file is not None:
                    with NamedTemporaryFile(suffix="pdf") as temp:
                        # st.write(temp)
                        # st.write(st.session_state.pdf_file.getvalue())
                        temp.write(st.session_state.pdf_file.getvalue())
                        temp.seek(0)
                        loader = PyPDFLoader(temp.name)
                        pdf = loader.load()
                        st.session_state.conversation = process_file(pdf)
                        print({"session_conversation": st.session_state.conversation})
                        st.markdown("Done processing. You may now ask a question.")

    ## T7: Handle query and display pages


if __name__ == "__main__":
    main()
