# المساعد العربي (Arabic Assistant)

A RAG-based Arabic chatbot that uses Gemini AI and FAISS for semantic search to provide accurate answers to user queries.

## Features

- Arabic language support with proper RTL display
- Semantic search using FAISS
- Integration with Google's Gemini AI
- FastAPI backend with CORS enabled for frontend communication
- PDF document processing and chunking
- React frontend for a modern user interface

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Node.js and npm (for the React frontend)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/MohamedREDA-24/Arabic_chatbot_RAG.git
cd Arabic_chatbot_RAG
```

2. Create and activate a Python virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the Python required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory and add your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

5. **Setup the React Frontend**
   Navigate to the `frontend` directory and install dependencies:
   ```bash
   cd frontend
   npm install
   ```
   Create a `.env` file inside the `frontend` directory with the following content:
   ```
   REACT_APP_API_URL=http://localhost:8000
   ```

## Usage

1. Start the FastAPI backend:
   Navigate to the root directory of the project:
   ```bash
   cd ..
   ```
   Then run:
```bash
python main.py
```
The API will be available at `http://localhost:8000`

2. In a new terminal, navigate to the `frontend` directory and start the React development server:
```bash
cd frontend
npm start
```
The React UI will open in your default web browser, usually at `http://localhost:3000`.

Interact with the chatbot using the React interface.

*(The original Streamlit UI is still available by running `streamlit run streamlit_app.py` from the root directory, but the primary frontend is now the React application)*.

## Project Structure

- `main.py`: FastAPI backend with RAG implementation and CORS
- `streamlit_app.py`: Original Streamlit frontend interface
- `requirements.txt`: Python project dependencies
- `document.pdf`: Sample document for testing
- `frontend/`: Contains the React frontend application
  - `frontend/package.json`: Frontend dependencies
  - `frontend/src/`: Frontend source files
  - `frontend/public/`: Frontend public assets
  - `frontend/.env`: Frontend environment variables
  - `frontend/README.md`: Frontend specific README

## API Endpoints

- `POST /query`: Submit a question and get an answer
  - Request body: `{"query": "your question here"}`
  - Response: `{"answer": "answer text", "sources": [...]}`
- `POST /feedback`: Submit feedback on an answer
  - Request body: `{"query": "...", "answer": "...", "feedback": true/false, "comment": "..." (optional)}`
  - Response: `{"status": "success", "message": "..."}`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Gemini AI
- FAISS for semantic search
- Streamlit for the UI framework
- FastAPI for the backend framework