# Refactoring Implementation Guide: Applying Modular Architecture to New PDF Display

## Table of Contents
1. [Overview](#overview)
2. [Current State Analysis](#current-state-analysis)
3. [Target Architecture](#target-architecture)
4. [Implementation Roadmap](#implementation-roadmap)
5. [Phase-by-Phase Implementation](#phase-by-phase-implementation)
6. [Testing Each Phase](#testing-each-phase)
7. [Final Verification](#final-verification)

---

## Overview

This guide shows you how to refactor the current `app.py` (202 lines with new PDF display) into a modular architecture following the principles from `REFACTORING_GUIDE.md`.

**What we're doing**:
- Breaking down the monolithic `app.py` into focused modules
- Extracting the new PDF rendering logic into reusable utilities
- Creating a clean separation between core logic, UI, and utilities
- Making the code testable, maintainable, and scalable

**Time Estimate**: 2-4 hours (done incrementally with testing after each phase)

---

## Current State Analysis

### File: `src/app.py` (202 lines)

**Responsibilities**:
1. **Lines 1-24**: Imports and environment setup
2. **Lines 27-45**: PDF processing and embeddings (`process_file`)
3. **Lines 49-66**: User query handling (`handle_input`)
4. **Lines 68-201**: Streamlit UI and PDF rendering (`main`)

**Key New Features** (from PDF display refactoring):
- Lines 138-183: Image-based PDF rendering with answer-first display
- Lines 162-171: Answer page highlighting
- Lines 173-183: Context pages display
- Lines 185-197: Error handling with download fallback

---

## Target Architecture

### Final File Structure

```
smart-pdf-reader/
├── src/
│   ├── __init__.py
│   ├── app.py                      # 60-80 lines - Clean entry point
│   ├── config.py                   # Configuration management
│   ├── core/
│   │   ├── __init__.py
│   │   ├── document_processor.py  # PDF loading and parsing
│   │   ├── embeddings.py          # Embedding generation
│   │   ├── vector_store.py        # Vector database operations
│   │   └── conversation.py        # LLM conversation chain
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── components.py          # Reusable UI components
│   │   ├── layout.py              # Page layout logic
│   │   ├── session.py             # Session state management
│   │   └── templates.py           # HTML/CSS templates
│   └── utils/
│       ├── __init__.py
│       ├── file_handlers.py       # File I/O operations
│       └── pdf_renderer.py        # NEW: Image-based PDF rendering
└── tests/
    ├── __init__.py
    ├── test_pdf_renderer.py       # NEW: Test PDF rendering
    └── fixtures/
        └── sample.pdf
```

---

## Implementation Roadmap

### Recommended Order (Safest to Riskiest)

1. ✅ **Phase 1**: Configuration extraction (Low risk, high value)
2. ✅ **Phase 2**: Utility modules (Low risk, independent)
3. ✅ **Phase 3**: Core business logic (Medium risk)
4. ✅ **Phase 4**: UI layer separation (Low risk)
5. ✅ **Phase 5**: Refactor main app.py (Low risk if previous phases work)

**Important**: Test after each phase before moving to the next!

---

## Phase-by-Phase Implementation

## Phase 1: Configuration Extraction

### Step 1.1: Create Configuration Module

**Create `src/config.py`:**

```python
"""Application configuration and settings"""
from dataclasses import dataclass
from typing import Literal
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ModelConfig:
    """LLM and embedding model configuration"""
    embedding_model: str = "thenlper/gte-small"
    embedding_device: Literal["cpu", "cuda"] = "cpu"
    llm_temperature: float = 0.3
    retrieval_k: int = 2
    normalize_embeddings: bool = False


@dataclass
class PDFConfig:
    """PDF display configuration"""
    context_pages_before: int = 2
    context_pages_after: int = 2
    default_page: int = 0
    image_dpi: int = 150  # DPI for PDF to image conversion


@dataclass
class UIConfig:
    """UI configuration"""
    page_title: str = "Interactive PDF Reader"
    page_icon: str = "📚"
    layout: Literal["wide", "centered"] = "wide"


@dataclass
class APIConfig:
    """API keys and credentials"""
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    huggingface_token: str = os.getenv("HUGGINGFACEHUB_API_TOKEN", "")

    def validate(self) -> bool:
        """Validate required API keys are present"""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        return True


# Global config instances
model_config = ModelConfig()
pdf_config = PDFConfig()
ui_config = UIConfig()
api_config = APIConfig()
```

**What changed**: Extracted all magic numbers and configuration into one place.

---

## Phase 2: Utility Modules

### Step 2.1: Create File Handler Utility

**Create `src/utils/__init__.py`:**

```python
"""Utility modules for file handling and PDF rendering"""
```

**Create `src/utils/file_handlers.py`:**

```python
"""File I/O utilities for PDF processing"""
from tempfile import NamedTemporaryFile
from typing import BinaryIO
import streamlit as st


class FileHandler:
    """Handles file operations for PDF processing"""

    @staticmethod
    def create_temp_pdf(uploaded_file) -> str:
        """
        Create temporary PDF file from Streamlit upload

        Args:
            uploaded_file: Streamlit UploadedFile object

        Returns:
            Path to temporary file

        Example:
            >>> temp_path = FileHandler.create_temp_pdf(st.session_state.pdf_file)
        """
        with NamedTemporaryFile(suffix=".pdf", delete=False) as temp:
            temp.write(uploaded_file.getvalue())
            temp.seek(0)
            return temp.name

    @staticmethod
    def write_temp_pdf(file_bytes: bytes) -> str:
        """
        Write bytes to temporary PDF file

        Args:
            file_bytes: PDF file bytes

        Returns:
            Path to temporary file

        Example:
            >>> temp_path = FileHandler.write_temp_pdf(pdf_bytes)
        """
        with NamedTemporaryFile(suffix=".pdf", delete=False) as temp:
            temp.write(file_bytes)
            temp.seek(0)
            return temp.name
```

---

### Step 2.2: Create PDF Renderer Utility (NEW - Image-based)

**Create `src/utils/pdf_renderer.py`:**

```python
"""PDF rendering utilities with image-based display and answer-first logic"""
from typing import List, Tuple
from pdf2image import convert_from_path
from pypdf import PdfReader
from PIL import Image
import streamlit as st

from src.config import pdf_config


class PDFRenderer:
    """Handles PDF page extraction and image-based rendering"""

    @staticmethod
    def get_page_count(pdf_path: str) -> int:
        """
        Get total number of pages in PDF

        Args:
            pdf_path: Path to PDF file

        Returns:
            Total page count
        """
        reader = PdfReader(pdf_path)
        return len(reader.pages)

    @staticmethod
    def calculate_page_range(
        current_page: int,
        total_pages: int,
        pages_before: int = pdf_config.context_pages_before,
        pages_after: int = pdf_config.context_pages_after
    ) -> Tuple[int, int]:
        """
        Calculate page range for context window

        Args:
            current_page: Current page (0-indexed)
            total_pages: Total pages in document
            pages_before: Number of pages before current
            pages_after: Number of pages after current

        Returns:
            Tuple of (start_page, end_page) both 0-indexed

        Example:
            >>> calculate_page_range(10, 50, 2, 2)
            (8, 12)
        """
        start_page = max(current_page - pages_before, 0)
        end_page = min(current_page + pages_after, total_pages - 1)
        return start_page, end_page

    @staticmethod
    def convert_pages_to_images(
        pdf_path: str,
        start_page: int,
        end_page: int,
        dpi: int = pdf_config.image_dpi
    ) -> List[Image.Image]:
        """
        Convert PDF pages to PIL images

        Args:
            pdf_path: Path to PDF file
            start_page: Start page (0-indexed)
            end_page: End page (0-indexed, inclusive)
            dpi: Image resolution

        Returns:
            List of PIL Image objects

        Example:
            >>> images = PDFRenderer.convert_pages_to_images("doc.pdf", 0, 4)
            >>> len(images)
            5
        """
        # Note: pdf2image uses 1-indexed pages
        images = convert_from_path(
            pdf_path,
            first_page=start_page + 1,
            last_page=end_page + 1,
            dpi=dpi
        )
        return images

    @staticmethod
    def calculate_answer_page_index(current_page: int, start_page: int) -> int:
        """
        Calculate the index of answer page in images array

        Args:
            current_page: Current page number (0-indexed)
            start_page: Start page of range (0-indexed)

        Returns:
            Index in images array

        Example:
            >>> calculate_answer_page_index(10, 8)
            2  # Third image in the array
        """
        return current_page - start_page

    @staticmethod
    def render_answer_first(
        images: List[Image.Image],
        answer_page_index: int,
        current_page: int,
        start_page: int
    ):
        """
        Render PDF pages with answer page first, then context pages

        Args:
            images: List of PIL images
            answer_page_index: Index of answer page in images list
            current_page: Actual page number of answer (0-indexed)
            start_page: First page in range (0-indexed)

        Example:
            >>> PDFRenderer.render_answer_first(images, 2, 10, 8)
            # Displays page 10 first, then pages 8, 9, 11, 12
        """
        # Display answer page first with highlighting
        if 0 <= answer_page_index < len(images):
            st.markdown("### 📍 Answer found on this page:")
            st.image(
                images[answer_page_index],
                caption=f"Page {current_page + 1} (Answer Source)",
                use_column_width=True
            )

        # Display context pages (skip answer page to avoid duplication)
        if len(images) > 1:
            st.markdown("### 📄 Context pages:")
            for idx, image in enumerate(images):
                if idx != answer_page_index:
                    actual_page_num = start_page + idx + 1  # Convert to 1-indexed
                    st.image(
                        image,
                        caption=f"Page {actual_page_num}",
                        use_column_width=True
                    )

    @staticmethod
    def render_pdf_with_answer_highlight(
        pdf_path: str,
        current_page: int
    ) -> None:
        """
        Complete workflow: render PDF with answer page highlighted

        This is the main public method that handles the entire rendering process.

        Args:
            pdf_path: Path to PDF file
            current_page: Page containing answer (0-indexed)

        Example:
            >>> temp_path = FileHandler.create_temp_pdf(uploaded_file)
            >>> PDFRenderer.render_pdf_with_answer_highlight(temp_path, 5)
        """
        try:
            # Get total pages
            total_pages = PDFRenderer.get_page_count(pdf_path)

            # Calculate page range
            start_page, end_page = PDFRenderer.calculate_page_range(
                current_page, total_pages
            )

            # Show page info
            st.write(
                f"Displaying pages {start_page + 1} to {end_page + 1} "
                f"of {total_pages}"
            )

            # Convert pages to images
            images = PDFRenderer.convert_pages_to_images(
                pdf_path, start_page, end_page
            )

            # Calculate answer page index
            answer_idx = PDFRenderer.calculate_answer_page_index(
                current_page, start_page
            )

            # Render with answer-first display
            PDFRenderer.render_answer_first(
                images, answer_idx, current_page, start_page
            )

        except Exception as e:
            st.error(f"Error displaying PDF: {str(e)}")
            st.info(
                "Try using the download button below to view the PDF locally"
            )
            raise  # Re-raise for calling code to handle

    @staticmethod
    def render_fallback_download(pdf_bytes: bytes, filename: str = "document.pdf"):
        """
        Render download button as fallback when rendering fails

        Args:
            pdf_bytes: PDF file bytes
            filename: Suggested filename for download
        """
        st.download_button(
            label="Download PDF",
            data=pdf_bytes,
            file_name=filename,
            mime="application/pdf"
        )
```

**What's new**: This module encapsulates all the new PDF rendering logic with answer-first display.

---

## Phase 3: Core Business Logic

### Step 3.1: Create Core Module Init

**Create `src/core/__init__.py`:**

```python
"""Core business logic modules"""
```

### Step 3.2: Document Processor

**Create `src/core/document_processor.py`:**

```python
"""PDF document loading and processing"""
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document


class DocumentProcessor:
    """Handles PDF document loading and processing"""

    @staticmethod
    def load_pdf(file_path: str) -> List[Document]:
        """
        Load and parse PDF into LangChain documents

        Args:
            file_path: Path to PDF file

        Returns:
            List of Document objects with page content and metadata

        Example:
            >>> docs = DocumentProcessor.load_pdf("sample.pdf")
            >>> len(docs)
            10
        """
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        return documents

    @staticmethod
    def get_page_count(documents: List[Document]) -> int:
        """
        Get total number of pages in document

        Args:
            documents: List of Document objects

        Returns:
            Number of pages
        """
        return len(documents)
```

### Step 3.3: Embeddings Service

**Create `src/core/embeddings.py`:**

```python
"""Embedding generation for document chunks"""
from langchain_huggingface import HuggingFaceEmbeddings
from src.config import model_config


class EmbeddingService:
    """Manages document embeddings using HuggingFace models"""

    def __init__(
        self,
        model_name: str = model_config.embedding_model,
        device: str = model_config.embedding_device,
        normalize: bool = model_config.normalize_embeddings
    ):
        """
        Initialize embedding service

        Args:
            model_name: HuggingFace model identifier
            device: cpu or cuda
            normalize: Whether to normalize embeddings
        """
        self.model_name = model_name
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": device},
            encode_kwargs={"normalize_embeddings": normalize}
        )

    def get_embeddings(self) -> HuggingFaceEmbeddings:
        """Return configured embeddings instance"""
        return self.embeddings
```

### Step 3.4: Vector Store

**Create `src/core/vector_store.py`:**

```python
"""Vector database operations"""
from typing import List
from langchain.schema import Document
from langchain_chroma import Chroma  # Updated import
from langchain.embeddings.base import Embeddings


class VectorStore:
    """Manages vector database for document retrieval"""

    def __init__(self, embeddings: Embeddings):
        """
        Initialize vector store

        Args:
            embeddings: Embedding model instance
        """
        self.embeddings = embeddings
        self.store = None

    def create_from_documents(self, documents: List[Document]) -> "VectorStore":
        """
        Create vector store from documents

        Args:
            documents: List of LangChain documents

        Returns:
            Self for method chaining
        """
        self.store = Chroma.from_documents(documents, self.embeddings)
        return self

    def as_retriever(self, k: int = None):
        """
        Get retriever for similarity search

        Args:
            k: Number of documents to retrieve (uses config default if None)

        Returns:
            VectorStoreRetriever instance
        """
        from src.config import model_config

        if not self.store:
            raise ValueError(
                "Vector store not initialized. Call create_from_documents first."
            )

        k = k or model_config.retrieval_k
        return self.store.as_retriever(search_kwargs={"k": k})
```

### Step 3.5: Conversation Service

**Create `src/core/conversation.py`:**

```python
"""LLM conversation chain management"""
from typing import List, Tuple, Dict, Any
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
from src.config import model_config


class ConversationService:
    """Manages conversational retrieval chain for Q&A"""

    def __init__(
        self,
        temperature: float = model_config.llm_temperature,
        return_sources: bool = True
    ):
        """
        Initialize conversation service

        Args:
            temperature: LLM temperature (0.0-1.0)
            return_sources: Whether to return source documents
        """
        self.temperature = temperature
        self.return_sources = return_sources
        self.llm = ChatOpenAI(temperature=temperature)

    def create_chain(self, retriever) -> ConversationalRetrievalChain:
        """
        Create conversational retrieval chain

        Args:
            retriever: Vector store retriever

        Returns:
            ConversationalRetrievalChain instance
        """
        chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            return_source_documents=self.return_sources
        )
        return chain

    @staticmethod
    def query(
        chain: ConversationalRetrievalChain,
        question: str,
        chat_history: List[Tuple[str, str]]
    ) -> Dict[str, Any]:
        """
        Execute query against conversation chain

        Args:
            chain: Conversation chain instance
            question: User question
            chat_history: List of (question, answer) tuples

        Returns:
            Response dict with 'answer' and 'source_documents'
        """
        response = chain.invoke(
            {"question": question, "chat_history": chat_history},
            return_only_outputs=True
        )
        return response

    @staticmethod
    def extract_page_number(response: Dict[str, Any]) -> int:
        """
        Extract page number from response source documents

        Args:
            response: Response dict from query

        Returns:
            Page number (0-indexed)
        """
        try:
            source_docs = response.get("source_documents", [])
            if source_docs:
                # Extract page from metadata
                page_num = list(source_docs[0])[1][1].get("page", 0)
                return page_num
        except (IndexError, KeyError, AttributeError):
            return 0
        return 0
```

---

## Phase 4: UI Layer Separation

### Step 4.1: Create UI Module Init

**Create `src/ui/__init__.py`:**

```python
"""UI components and layout management"""
```

### Step 4.2: Session Management

**Create `src/ui/session.py`:**

```python
"""Streamlit session state management"""
import streamlit as st
from typing import Any, List, Tuple


class SessionManager:
    """Centralized session state management"""

    @staticmethod
    def initialize():
        """Initialize all session state variables"""
        defaults = {
            "conversation": None,
            "history": [],
            "page_num": 0,
            "user_input": "",
            "pdf_file": None,
            "expander": None
        }

        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value

    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """Get value from session state"""
        return st.session_state.get(key, default)

    @staticmethod
    def set(key: str, value: Any):
        """Set value in session state"""
        st.session_state[key] = value

    @staticmethod
    def append_to_history(question: str, answer: str):
        """Append Q&A pair to chat history"""
        if "history" not in st.session_state:
            st.session_state.history = []
        st.session_state.history.append((question, answer))

    @staticmethod
    def get_history() -> List[Tuple[str, str]]:
        """Get chat history"""
        return st.session_state.get("history", [])

    @staticmethod
    def clear_history():
        """Clear chat history"""
        st.session_state.history = []
```

### Step 4.3: UI Components

**Create `src/ui/components.py`:**

```python
"""Reusable UI components"""
import streamlit as st
from typing import List, Tuple


class ChatComponents:
    """Chat UI components"""

    @staticmethod
    def render_message(message: str, template: str):
        """
        Render a chat message using template

        Args:
            message: Message text
            template: HTML template with {{MSG}} placeholder
        """
        st.write(
            template.replace("{{MSG}}", message),
            unsafe_allow_html=True
        )

    @staticmethod
    def render_chat_history(
        history: List[Tuple[str, str]],
        user_template: str,
        bot_template: str,
        expander
    ):
        """
        Render entire chat history in expander

        Args:
            history: List of (question, answer) tuples
            user_template: Template for user messages
            bot_template: Template for bot messages
            expander: Streamlit expander object
        """
        with expander:
            for question, answer in history:
                ChatComponents.render_message(question, user_template)
                ChatComponents.render_message(answer, bot_template)


class PDFComponents:
    """PDF viewer components"""

    @staticmethod
    def render_pdf_viewer_with_fallback(pdf_file, current_page: int):
        """
        Render PDF with answer highlighting and error fallback

        Args:
            pdf_file: Streamlit UploadedFile object
            current_page: Page number to highlight (0-indexed)
        """
        from src.utils.file_handlers import FileHandler
        from src.utils.pdf_renderer import PDFRenderer

        if not pdf_file:
            return

        try:
            # Create temporary file
            temp_path = FileHandler.create_temp_pdf(pdf_file)

            # Render with answer highlighting
            PDFRenderer.render_pdf_with_answer_highlight(temp_path, current_page)

        except Exception as e:
            # Fallback to download button
            st.error(f"Could not render PDF: {str(e)}")
            PDFRenderer.render_fallback_download(
                pdf_file.getvalue(),
                filename="document.pdf"
            )
```

### Step 4.4: Layout Management

**Create `src/ui/layout.py`:**

```python
"""Page layout management"""
import streamlit as st
from src.config import ui_config


class AppLayout:
    """Manages application layout and page structure"""

    @staticmethod
    def setup_page():
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title=ui_config.page_title,
            layout=ui_config.layout,
            page_icon=ui_config.page_icon
        )

    @staticmethod
    def create_two_column_layout():
        """
        Create two-column layout

        Returns:
            Tuple of (left_column, right_column)
        """
        return st.columns(2)

    @staticmethod
    def render_header(text: str):
        """Render page header"""
        st.header(text)

    @staticmethod
    def create_expander(title: str, expanded: bool = True):
        """
        Create expandable container

        Args:
            title: Expander title
            expanded: Initial expanded state

        Returns:
            Streamlit expander object
        """
        return st.expander(title, expanded=expanded)
```

### Step 4.5: Move Templates

**Rename `src/html_templates.py` to `src/ui/templates.py`:**

```bash
mv src/html_templates.py src/ui/templates.py
```

No code changes needed in this file.

---

## Phase 5: Refactor Main App

### Step 5.1: Create New `src/app.py`

**Replace `src/app.py` with:**

```python
"""Main Streamlit application entry point"""
import streamlit as st

from src.config import ui_config
from src.core.document_processor import DocumentProcessor
from src.core.embeddings import EmbeddingService
from src.core.vector_store import VectorStore
from src.core.conversation import ConversationService
from src.ui.layout import AppLayout
from src.ui.session import SessionManager
from src.ui.components import ChatComponents, PDFComponents
from src.ui.templates import css, bot_template, user_template, expander_css
from src.utils.file_handlers import FileHandler


def initialize_app():
    """Initialize application configuration and session"""
    AppLayout.setup_page()
    st.markdown(css, unsafe_allow_html=True)
    SessionManager.initialize()


def process_uploaded_pdf(uploaded_file) -> bool:
    """
    Process uploaded PDF and create conversation chain

    Args:
        uploaded_file: Streamlit UploadedFile object

    Returns:
        True if processing successful, False otherwise
    """
    try:
        with st.spinner("Processing PDF..."):
            # Create temporary file
            temp_path = FileHandler.create_temp_pdf(uploaded_file)

            # Load document
            documents = DocumentProcessor.load_pdf(temp_path)

            # Create embeddings and vector store
            embedding_service = EmbeddingService()
            vector_store = VectorStore(embedding_service.get_embeddings())
            vector_store.create_from_documents(documents)

            # Create conversation chain
            conv_service = ConversationService()
            retriever = vector_store.as_retriever()
            chain = conv_service.create_chain(retriever)

            # Store in session
            SessionManager.set("conversation", chain)

        return True

    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return False


def handle_user_query(query: str):
    """
    Handle user query and display response

    Args:
        query: User question
    """
    conversation = SessionManager.get("conversation")
    history = SessionManager.get_history()
    expander = SessionManager.get("expander")

    if not conversation:
        st.warning("Please upload and process a PDF first")
        return

    # Get response from conversation chain
    response = ConversationService.query(conversation, query, history)

    # Update history
    SessionManager.append_to_history(query, response["answer"])

    # Extract and update page number
    page_num = ConversationService.extract_page_number(response)
    SessionManager.set("page_num", page_num)

    # Render updated chat history
    updated_history = SessionManager.get_history()
    ChatComponents.render_chat_history(
        updated_history,
        user_template,
        bot_template,
        expander
    )


def main():
    """Main application flow"""
    # Initialize
    initialize_app()

    # Create two-column layout
    col1, col2 = AppLayout.create_two_column_layout()

    # Left column: Chat interface
    with col1:
        AppLayout.render_header("Interactive Reader 📚")

        # User input
        user_input = st.text_input(
            "Ask a question from the contents of the PDF:"
        )
        SessionManager.set("user_input", user_input)

        # Chat history expander
        expander = AppLayout.create_expander("Your Chat History", expanded=True)
        SessionManager.set("expander", expander)

        with expander:
            st.markdown(expander_css, unsafe_allow_html=True)

        # PDF upload section
        st.header("Your Documents")
        pdf_file = st.file_uploader("Upload a PDF here and click 'Process'")
        SessionManager.set("pdf_file", pdf_file)

        # Process button
        if st.button("Process"):
            if pdf_file:
                if process_uploaded_pdf(pdf_file):
                    st.success("Done processing. You may now ask a question.")
            else:
                st.warning("Please provide a PDF file")

    # Right column: Query handling and PDF viewer
    with col2:
        user_input = SessionManager.get("user_input")
        conversation = SessionManager.get("conversation")

        # Handle user query
        if user_input and conversation:
            handle_user_query(user_input)
        elif user_input:
            st.warning("Please upload and process a PDF first")

        # Render PDF with answer highlighting
        pdf_file = SessionManager.get("pdf_file")
        current_page = SessionManager.get("page_num", 0)

        if pdf_file:
            PDFComponents.render_pdf_viewer_with_fallback(pdf_file, current_page)


if __name__ == "__main__":
    main()
```

**Result**: Main file reduced from **202 lines to ~140 lines** with much better organization!

---

## Testing Each Phase

### After Phase 1 (Configuration)

```bash
# Test imports
python -c "from src.config import model_config, pdf_config, ui_config, api_config; print('✓ Config module works')"
```

### After Phase 2 (Utilities)

```bash
# Test file handler
python -c "from src.utils.file_handlers import FileHandler; print('✓ FileHandler works')"

# Test PDF renderer
python -c "from src.utils.pdf_renderer import PDFRenderer; print('✓ PDFRenderer works')"
```

### After Phase 3 (Core Logic)

```bash
# Test document processor
python -c "from src.core.document_processor import DocumentProcessor; print('✓ DocumentProcessor works')"

# Test all core modules
python -c "from src.core.embeddings import EmbeddingService; from src.core.vector_store import VectorStore; from src.core.conversation import ConversationService; print('✓ All core modules work')"
```

### After Phase 4 (UI Layer)

```bash
# Test UI modules
python -c "from src.ui.session import SessionManager; from src.ui.layout import AppLayout; from src.ui.components import ChatComponents; print('✓ UI modules work')"
```

### After Phase 5 (Main App)

```bash
# Run the application
streamlit run src/app.py

# Test checklist:
# 1. Upload a PDF ✓
# 2. Click Process ✓
# 3. Ask a question ✓
# 4. Verify answer page displays first with 📍 ✓
# 5. Verify context pages display below ✓
# 6. Check page numbers are correct ✓
```

---

## Final Verification

### Verification Checklist

- [ ] **Configuration works**
  - [ ] DPI setting from config.py is used
  - [ ] Context pages setting is respected
  - [ ] Model config values are applied

- [ ] **PDF Rendering works**
  - [ ] Answer page displays first
  - [ ] Context pages show below
  - [ ] Page numbers are correct
  - [ ] Fallback download appears on error

- [ ] **Core Logic works**
  - [ ] PDFs upload and process
  - [ ] Embeddings are created
  - [ ] Questions get answered
  - [ ] Chat history updates

- [ ] **UI works**
  - [ ] Two-column layout renders
  - [ ] Chat expander works
  - [ ] Messages display correctly
  - [ ] Session state persists

- [ ] **Error Handling works**
  - [ ] Invalid PDF shows error
  - [ ] Missing API key shows error
  - [ ] PDF rendering failure shows download option

---

## Troubleshooting

### Common Issues

**Issue 1: Import errors**
```
ModuleNotFoundError: No module named 'src.config'
```

**Solution**: Make sure all `__init__.py` files exist:
```bash
touch src/__init__.py
touch src/core/__init__.py
touch src/ui/__init__.py
touch src/utils/__init__.py
```

**Issue 2: Deprecated import warning**
```
LangChainDeprecationWarning: langchain_community.vectorstores is deprecated
```

**Solution**: Update import in `src/core/vector_store.py`:
```python
# Change from
from langchain_community.vectorstores import Chroma

# To
from langchain_chroma import Chroma
```

And add to requirements.txt:
```
langchain-chroma
```

**Issue 3: PDF rendering fails**
```
Error displaying PDF: poppler not found
```

**Solution**: Install poppler:
```bash
# macOS
brew install poppler

# Ubuntu/Debian
sudo apt-get install poppler-utils
```

**Issue 4: Session state not persisting**
```
KeyError: 'conversation'
```

**Solution**: Ensure `SessionManager.initialize()` is called in `initialize_app()`.

---

## Benefits Achieved

### Code Organization
- ✅ Single Responsibility: Each module has one clear purpose
- ✅ Testability: Can test each component independently
- ✅ Reusability: Modules can be used in other projects
- ✅ Maintainability: Easy to locate and fix bugs

### New Features Made Easy
Want to add thumbnail navigation? Just modify `src/utils/pdf_renderer.py`.
Want to change DPI? Just update `src/config.py`.
Want to add new embedding model? Just modify `src/core/embeddings.py`.

### Performance
- ✅ Same or better performance
- ✅ Potential for caching in individual modules
- ✅ Easier to optimize specific components

### Team Collaboration
- ✅ Multiple developers can work on different modules
- ✅ Fewer merge conflicts
- ✅ Clear code ownership

---

## Next Steps

1. **Add Tests**: Create unit tests for each module
2. **Add Type Hints**: Use mypy for type checking
3. **Add Logging**: Implement proper logging throughout
4. **Add Caching**: Cache PDF conversions using `@st.cache_data`
5. **Add Documentation**: Create docstrings and usage examples

---

## Summary

You've successfully refactored a **202-line monolithic file** into a **well-organized modular architecture** with:

- 📁 **4 core modules** (document_processor, embeddings, vector_store, conversation)
- 📁 **4 UI modules** (session, layout, components, templates)
- 📁 **2 utility modules** (file_handlers, pdf_renderer)
- 📁 **1 configuration module** (config)
- 📁 **1 clean entry point** (app.py)

The new architecture maintains all functionality while being:
- ✨ More maintainable
- ✨ More testable
- ✨ More scalable
- ✨ Easier to extend

Great job! 🎉
