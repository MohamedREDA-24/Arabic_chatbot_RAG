# المساعد العربي (Arabic Assistant)

A RAG-based Arabic chatbot that uses Gemini AI and FAISS for semantic search to provide accurate answers to user queries.

## Features

- Arabic language support with proper RTL display
- Semantic search using FAISS
- Integration with Google's Gemini AI
- Clean and modern Streamlit UI
- FastAPI backend for efficient processing
- PDF document processing and chunking

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd Arabic_chatbot_RAG
```

2. Create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory and add your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

## Usage

1. Start the FastAPI backend:
```bash
python main.py
```
The API will be available at `http://localhost:8000`

2. In a new terminal, start the Streamlit UI:
```bash
streamlit run streamlit_app.py
```
The UI will open in your default web browser at `http://localhost:8501`

3. Enter your questions in Arabic and get instant answers!

## Project Structure

- `main.py`: FastAPI backend with RAG implementation
- `streamlit_app.py`: Streamlit frontend interface
- `requirements.txt`: Project dependencies
- `document.pdf`: Sample document for testing

## API Endpoints

- `POST /query`: Submit a question and get an answer
  - Request body: `{"query": "your question here"}`
  - Response: `{"answer": "answer text", "sources": [...]}`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Gemini AI
- FAISS for semantic search
- Streamlit for the UI framework
- FastAPI for the backend framework