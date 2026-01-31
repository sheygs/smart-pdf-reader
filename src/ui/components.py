import html

import streamlit as st
from ui.html_templates import bot_template, user_template


class ChatComponents:

    @staticmethod
    def render_message(message: str, is_user: bool = False):
        template = user_template if is_user else bot_template
        safe_message = html.escape(message)  # Sanitize to prevent XSS
        st.write(template.replace("{{MSG}}", safe_message), unsafe_allow_html=True)

    @staticmethod
    def render_chat_history(history: list):
        for question, answer in history:
            ChatComponents.render_message(question, True)
            ChatComponents.render_message(answer, is_user=False)


class PDFComponents:

    @staticmethod
    def render_pdf_images(
        images: list,
        answer_page_index: int,
        start_page: int,
        end_page: int,
        total_pages: int,
        current_page: int,
    ):
        st.write(
            f"Displaying pages {start_page + 1} to {end_page + 1} of {total_pages}"
        )

        if 0 <= answer_page_index < len(images):
            st.markdown("### 📍 Answer found on this page:")
            st.image(
                images[answer_page_index],
                caption=f"Page {current_page + 1} (Answer Source)",
                width="stretch",
            )

        if len(images) > 1:
            st.markdown("### 📄 Context pages:")
            for idx, image in enumerate(images):
                if idx != answer_page_index:
                    st.image(
                        image,
                        caption=f"Page {start_page + idx + 1}",
                        width="stretch",
                    )
