from tempfile import NamedTemporaryFile
import streamlit as st


class FileHandler:
    """Handles file operations for PDF processing"""

    @staticmethod
    def create_temp_file(
        uploaded_file: st.runtime.uploaded_file_manager.UploadedFile,
        suffix: str = ".pdf",
    ):
        """
        Create temporary file from Streamlit upload

        Args:
            uploaded_file: Streamlit UploadedFile object
            suffix: File extension

        Returns:
            Path to temporary file
        """
        with NamedTemporaryFile(suffix, delete=False) as temp:
            temp.write(uploaded_file.getvalue())
            temp.seek(0)
            return temp

    @staticmethod
    def write_temp_pdf(file_bytes: bytes) -> str:
        """
        Write bytes to temporary PDF file

        Args:
            file_bytes: PDF file bytes

        Returns:
            Path to temporary file
        """
        with NamedTemporaryFile(suffix=".pdf", delete=False) as temp:
            temp.write(file_bytes)
            temp.seek(0)
            return temp.name
