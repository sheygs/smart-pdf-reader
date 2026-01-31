import os
from tempfile import NamedTemporaryFile
from typing import Optional
import streamlit as st


class FileHandler:
    # Track temp files for cleanup
    _temp_files: list = []

    @classmethod
    def create_temp_file(
        cls,
        uploaded_file: st.runtime.uploaded_file_manager.UploadedFile,
        suffix: str = ".pdf",
    ) -> str:
        """
        Create temporary file from Streamlit upload

        Args:
            uploaded_file: Streamlit UploadedFile object
            suffix: File extension

        Returns:
            Path to temporary file
        """
        with NamedTemporaryFile(suffix=suffix, delete=False) as temp:
            temp.write(uploaded_file.getvalue())
            temp.seek(0)
            cls._temp_files.append(temp.name)
            return temp.name

    @classmethod
    def cleanup_temp_files(cls) -> None:
        """Remove all tracked temporary files"""
        for temp_path in cls._temp_files:
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            except OSError:
                # file may already be deleted
                pass
        cls._temp_files.clear()

    @classmethod
    def cleanup_single_file(cls, file_path: Optional[str]) -> None:
        """Remove a single temporary file"""
        if file_path and os.path.exists(file_path):
            try:
                os.unlink(file_path)
                if file_path in cls._temp_files:
                    cls._temp_files.remove(file_path)
            except OSError:
                pass
