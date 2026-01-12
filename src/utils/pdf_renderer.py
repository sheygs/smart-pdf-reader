import base64
from pypdf import PdfReader, PdfWriter
from src.config import pdf_config


class PDFRenderer:
    """Handles PDF page extraction and rendering"""

    @staticmethod
    def pdf_to_base64(pdf_bytes: bytes) -> str:
        """
        Convert PDF bytes to base64 string

        Args:
            pdf_bytes: PDF file bytes

        Returns:
            Base64 encoded string
        """
        base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
        return base64_pdf

    @staticmethod
    def extract_pages_with_context(
        pdf_path: str,
        current_page: int,
        pages_before: int = pdf_config.context_page_before,
        pages_after: int = pdf_config.context_page_after,
    ) -> bytes:
        """
        Extract current page with surrounding context

        Args:
            pdf_path: Path to PDF file
            current_page: Current page number (0-indexed)
            pages_before: Number of pages before current
            pages_after: Number of pages after current

        Returns:
            PDF bytes containing extracted pages
        """
        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        start = max(current_page - pages_before, 0)
        end = min(current_page + pages_after, len(reader.pages) - 1)

        for page_num in (start, end + 1):
            writer.add_page(reader.pages[page_num])

        # while start <= end:
        #     writer.add_page(reader.pages[start])
        #     start += 1

        # Write to bytes
        from io import BytesIO

        output = BytesIO()
        writer.write(output)
        return output.getvalue()
