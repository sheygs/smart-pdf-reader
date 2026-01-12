import streamlit as st
from typing import Any


class SessionManager:
    @staticmethod
    def initialize():
        """Initialize all session state variables"""
        defaults = {
            "conversation": None,
            "history": [],
            "page_num": 0,
            "user_input": "",
            "expander": None,
            "pdf_file": None,
        }

        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    @staticmethod
    def set(key: str, value: Any):
        st.session_state[key] = value

    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        return st.session_state.get(key, default)

    @staticmethod
    def append_to_history(question: str, answer: str):
        """Append Q&A pair to chat history"""
        st.session_state.history.append((question, answer))

    @staticmethod
    def clear_history():
        st.session_state.history = []
