# Smart PDF Reader

An interactive PDF reader powered by LangChain and GPT that enables users to upload PDF documents and chat with an AI assistant to extract insights, answer questions, and navigate content intelligently.

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-🦜-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?logo=openai&logoColor=white)

## Features

- **PDF Upload**: Upload any PDF document for interactive analysis
- **AI-Powered Q&A**: Ask questions about your PDF content and get intelligent answers
- **Semantic Search**: Uses vector embeddings to find relevant content accurately
- **Conversational Memory**: Maintains chat history for context-aware follow-up questions
- **Answer-First PDF Display**: Highlights the exact page containing the answer with 📍 indicator, followed by context pages
- **Image-Based PDF Rendering**: Reliable cross-platform PDF viewing that works on all deployment environments
- **Smart Page Context**: Automatically displays surrounding pages (±2 pages) for better understanding
- **Conversational Interface**: Natural chat experience powered by GPT-3.5/GPT-4
- **Simple UI**: Clean, intuitive interface built with Streamlit
- **Modular Architecture**: Well-organized codebase with separation of concerns for easy maintenance and extension
- **Performance Optimized**: Cached PDF-to-image conversion for faster repeated access

## Technologies

- **[LangChain](https://python.langchain.com/)** - Framework for LLM application development
- **[Streamlit](https://streamlit.io/)** - Web application framework
- **[OpenAI GPT](https://openai.com/)** - Large language model for answer generation
- **[Chroma](https://www.trychroma.com/)** - Vector database for embeddings
- **[HuggingFace Transformers](https://huggingface.co/)** - Embedding models
- **[pdf2image](https://github.com/Belval/pdf2image)** - PDF to image conversion for reliable rendering
- **[Poppler](https://poppler.freedesktop.org/)** - PDF rendering engine

## Prerequisites

- Python 3.12 (recommended) or 3.10-3.13
- OpenAI API key
- HUGGINGFACE API token
- Poppler (system dependency for PDF rendering)

## Installation

1. **Clone the repository**

```bash
   git clone https://github.com/sheygs/smart-pdf-reader.git
   cd smart-pdf-reader
```

2. **Create a virtual environment**

```bash
   python3.12 -m venv venv
   source venv/bin/activate
```

3. **Install system dependencies**

   **For PDF rendering support**, install Poppler:
   - **macOS**:

     ```bash
     brew install poppler
     ```

   - **Linux (Ubuntu/Debian)**:

     ```bash
     sudo apt-get update
     sudo apt-get install -y poppler-utils
     ```

   - **Windows**:
     Download from [poppler releases](https://github.com/oschwartz10612/poppler-windows/releases/) and add to PATH

4. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**

   Rename the `.env.example` file to `.env` in the root directory and populate the required keys:

   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   HUGGINGFACEHUB_API_TOKEN=your_huggingface_api_token_here
   ```

## Usage

1. **Start the application**

```bash
   streamlit run src/app.py
```

2. **Upload your PDF**
   - Click on the file uploader in the sidebar
   - Select a PDF document from your local machine

3. **Process the PDF**
   - Click the "Process" button to analyze the document
   - Wait for the processing to complete

4. **Ask questions**
   - Type your question in the chat input
   - The AI will analyze the PDF and provide relevant answers
   - The answer page will be displayed first with a 📍 indicator
   - Context pages (±2 pages) will be shown below for additional context

## Project Structure

```text
smart-pdf-reader/
│
├── src/
│   ├── app.py                     # Main application entry point
│   ├── config.py                  # Configuration management
│   │
│   ├── core/                      # Core business logic
│   │   ├── conversation.py        # Conversation service (RAG chain)
│   │   ├── document_processor.py  # PDF document processing
│   │   ├── embeddings.py          # Embedding service
│   │   └── vector_store.py        # Vector database operations
│   │
│   ├── ui/                        # User interface components
│   │   ├── components.py          # Chat and PDF components
│   │   ├── html_templates.py      # HTML/CSS templates
│   │   ├── layout.py              # Application layout
│   │   └── session.py             # Session state management
│   │
│   └── utils/                     # Utility functions
│       ├── file_handlers.py       # File operations
│       └── pdf_renderer.py        # PDF rendering utilities
│
├── requirements.txt              # Python dependencies
├── .env.dev                      # Environment variables template
├── README.md                     # Project documentation
└── .gitignore
```

## How It Works

1. **PDF Processing**: Uploaded PDFs are parsed and split into manageable chunks using PyPDF
2. **Embedding Creation**: Text chunks are converted to vector embeddings using HuggingFace models (default: `thenlper/gte-small`)
3. **Vector Storage**: Embeddings are stored in Chroma vector database for efficient similarity search
4. **Conversational RAG**: Uses LangChain's retrieval chain with chat history awareness
5. **Query Processing**: User questions are contextualized with chat history and matched against stored vectors
6. **Answer Generation**: Relevant chunks are passed to GPT model with the contextualized question
7. **Answer-First Display**:
   - The page containing the answer is displayed first with a 📍 indicator
   - Surrounding pages (±2 pages) are shown below for context
   - PDF pages are converted to high-quality images (150 DPI) for reliable cross-platform rendering
   - Caching ensures fast repeated access to the same pages

## Architecture

The project follows a modular architecture pattern with clear separation of concerns:

- **Core Module** (`src/core/`): Business logic for document processing, embeddings, vector store, and conversation management
- **UI Module** (`src/ui/`): Streamlit interface components, layouts, and session management
- **Utils Module** (`src/utils/`): Reusable utilities for file handling and image-based PDF rendering
- **Config Module** (`src/config.py`): Centralized configuration and environment validation

### Key Design Decisions

- **Image-Based PDF Rendering**: Uses `pdf2image` instead of iframe embedding for reliable cross-platform display
- **Answer-First UX**: Displays the answer page prominently before showing context pages
- **Cached Rendering**: PDF-to-image conversion is cached using `@st.cache_data` for better performance
- **Configurable Context**: Context window (pages before/after answer) is configurable via `src/config.py`

## Configuration

You can customize the application behavior by modifying `src/config.py`:

```python
@dataclass
class PDFConfig:
    context_page_before: int = 2  # Pages to show before answer page
    context_page_after: int = 2   # Pages to show after answer page
    default_page: int = 0         # Default page to display
    dpi: int = 150                # Image resolution for PDF rendering
```

## Limitations

- **File Format Support**: Currently only supports PDF files. Support for other document formats (Word, TXT, etc.) is planned for future releases
- **Internet Connection Required**: Active internet connection needed for API calls to OpenAI and HuggingFace
- **API Costs**: OpenAI API usage incurs costs based on usage. Monitor your API usage to avoid unexpected charges
- **PDF Size**: Very large PDFs (100+ pages) may take longer to process and could impact performance
- **Language Support**: Best performance with English text. Other languages may work but have not been extensively tested
- **Memory Usage**: Processing large documents requires sufficient system memory. Close other applications if you experience slowdowns

## Contributing

Contributions are welcome! The project follows a modular architecture to make it easy to contribute:

1. **Core Features**: Add new functionality in the `src/core/` module
2. **UI Improvements**: Enhance the interface in the `src/ui/` module
3. **Utilities**: Add helper functions in the `src/utils/` module

## Acknowledgments

- OpenAI for GPT models
- LangChain team for the excellent framework
- Streamlit for the intuitive web framework
- HuggingFace for open-source embedding models

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
