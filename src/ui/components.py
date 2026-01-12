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
    def render_pdf_images(
        images: list,
        answer_page_index: int,
        start_page: int,
        end_page: int,
        total_pages: int,
        current_page: int,
    ):
        """
        Render PDF pages as images with answer page displayed first

        Args:
            images: List of PIL Image objects
            answer_page_index: Index of answer page in images list
            start_page: Starting page number (0-indexed)
            end_page: Ending page number (0-indexed)
            total_pages: Total number of pages in PDF
            current_page: Current page number (0-indexed)
        """
        st.write(
            f"Displaying pages {start_page + 1} to {end_page + 1} of {total_pages}"
        )

        # Display the answer page first (highlighted)
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
                # Skip the answer page we already showed
                if idx != answer_page_index:
                    st.image(
                        image,
                        caption=f"Page {start_page + idx + 1}",
                        width="stretch",
                    )
