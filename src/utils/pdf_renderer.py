from typing import List, Tuple
from pypdf import PdfReader
from pdf2image import convert_from_path
from PIL.Image import Image
from config import pdf_config


class PDFRenderer:
    """Handles PDF page extraction and rendering"""

    @staticmethod
    def convert_pages_to_images(
        pdf_path: str,
        current_page: int,
        pages_before: int = pdf_config.context_page_before,
        pages_after: int = pdf_config.context_page_after,
        dpi: int = 150,
    ) -> Tuple[List[Image], int, int, int, int]:
        """
        Convert PDF pages to images with context pages around current page

        Args:
            pdf_path: Path to PDF file
            current_page: Current page number (0-indexed)
            pages_before: Number of pages before current
            pages_after: Number of pages after current
            dpi: Resolution for image conversion

        Returns:
            Tuple of (images, start_page, end_page, total_pages, answer_page_index)
        """
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)

        start_page = max(current_page - pages_before, 0)
        end_page = min(current_page + pages_after, total_pages - 1)

        # Convert PDF pages to images (first_page is 1-indexed for pdf2image)
        images = convert_from_path(
            pdf_path,
            first_page=start_page + 1,
            last_page=end_page + 1,
            dpi=dpi,
        )

        # Calculate the answer page index within the images list
        answer_page_index = current_page - start_page

        return images, start_page, end_page, total_pages, answer_page_index
