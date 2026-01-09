## standard
from tempfile import NamedTemporaryFile
import base64
import os

# third-party
import streamlit as st
from dotenv import load_dotenv
# from langchain.embeddings import HuggingFaceEmbeddings, OpenAIEmbeddings
# from langchain.chat_models import ChatOpenAI
# from langchain.chains import ConversationalRetrievalChain
# from langchain.vectorstores import Chroma
# from langchain.document_loaders import PyPDFLoader
# from PyPDF2 import PdfReader, PdfWriter

# module imports
from html_templates import css, bot_template, user_template, expander_css

load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
huggingface_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")


## Todo 4: Process user input
def process_file():
    pass


## Todo 6: Method for Handling User Input
def handle_user_input():
    pass


def main():
    ## Todo 3: Create Web-page Layout
    st.set_page_config(
        page_title="Interactive PDF reader", layout="wide", page_icon="📕"
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

        with st.expander("Your Chat", expanded=True):
            st.markdown(expander_css, unsafe_allow_html=True)

    ## Todo 5: Load and Process the PDF
    ## Todo 7: Handle query and display pages


if __name__ == "__main__":
    main()
