import streamlit as st
from src.config import ui_config
from session import SessionManager


class AppLayout:

    @staticmethod
    def setup_page():
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title=ui_config.page_title,
            layout=ui_config.page_layout,
            page_icon=ui_config.page_icon,
        )

    @staticmethod
    def create_two_column_layout():
        """
        Create two-column layout

        Returns:
            Tuple of (left_column, right_column)
        """
        # return st.columns([1, 1])
        return st.columns(2)

    @staticmethod
    def render_header(text: str):
        """Render page header"""
        st.header(text)

    @staticmethod
    def create_chat_expander(text: str = "Your Chat History", expanded: bool = True):
        """
        Create expandable chat container

        Args:
            title: Expander title
            expanded: Initial expanded state

        Returns:
            Streamlit expander object
        """
        expander = st.expander(text, expanded=expanded)
        SessionManager.set("expander", expander)
        return expander
