import streamlit as st
from ui.html_templates import bot_template, user_template


class ChatComponents:
    @staticmethod
    def render_message(message: str, is_user: bool = False):
        """
        Render a chat message

        Args:
            message: Message text
            is_user: True for user message, False for bot
        """
        template = user_template if is_user else bot_template
        st.write(template.replace("{{MSG}}", message), unsafe_allow_html=True)

    @staticmethod
    def render_chat_hisotory(history: list):
        """
        Render entire chat history

        Args:
            history: List of (question, answer) tuples
        """
        for question, answer in history:
            ChatComponents.render_message(question, True)
            ChatComponents.render_message(answer, is_user=False)


class PDFComponents:
    @staticmethod
    def render_pdf_viewer(base64_pdf: str, page: int = 1, height: int = 900):
        pdf_display = f"""
        <iframe
            src="data:application/pdf;base64,
            {base64_pdf}#page={page}"
            width="100%"
            height="{height}"
            type="application/pdf"
            frameborder="0">
        </iframe>
        """
        st.markdown(pdf_display, unsafe_allow_html=True)
