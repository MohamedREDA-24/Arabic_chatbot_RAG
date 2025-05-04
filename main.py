from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import PyPDF2
import re
import google.generativeai as genai
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model_name = "models/gemini-1.5-pro-latest"
gemini = genai.GenerativeModel(model_name)

app = FastAPI(
    title="Arabic Legal Chatbot API",
    description="A RAG-based Arabic legal chatbot using Gemini and FAISS",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]

def normalize_arabic(text):
    text = re.sub(r'[أإآ]', 'ا', text)
    text = re.sub(r'[ى]', 'ي', text)
    text = re.sub(r'[ة]', 'ه', text)
    text = re.sub(r'[ً-ٟ]', '', text)
    text = re.sub(r'[^؀-ۿa-zA-Z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

#Read the data
def read_pdf(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"الملف {file_path} غير موجود")

    try:
        reader = PyPDF2.PdfReader(file_path)
        all_pages_text = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                all_pages_text.append(normalize_arabic(page_text))

        if not all_pages_text:
            raise ValueError("الملف لا يحتوي على نص قابل للقراءة")

        return all_pages_text
    except Exception as e:
        raise RuntimeError(f"خطأ في قراءة الملف: {str(e)}")

#Chunking
def semantic_chunking(pages_text, similarity_threshold=0.72):
    """تقسيم النص إلى أجزاء مترابطة دلاليًا"""
    chunks = []

    for text in pages_text:
        sentences = re.split(r'(?<=[.!؟])\s+', text)
        current_chunk = []
        prev_emb = None

        for i in range(0, len(sentences), 20):
            batch = [s.strip() for s in sentences[i:i+20] if s.strip()]

            if not batch:
                continue

            embeddings = get_embeddings(batch)
            if embeddings is None:
                continue

            for emb, sentence in zip(embeddings, batch):
                if prev_emb is not None:
                    similarity = np.dot(prev_emb, emb) / (np.linalg.norm(prev_emb) * np.linalg.norm(emb))
                    if similarity < similarity_threshold:
                        chunks.append(" ".join(current_chunk))
                        current_chunk = []
                current_chunk.append(sentence)
                prev_emb = emb

        if current_chunk:
            chunks.append(" ".join(current_chunk))

    return [c for c in chunks if c.strip()]

def get_embeddings(texts):
    try:
        response = genai.embed_content(
            model="models/embedding-001",
            content=texts,
            task_type="RETRIEVAL_DOCUMENT"
        )
        return np.array(response['embedding'], dtype='float32')
    except Exception as e:
        print(f"خطأ في التضمين: {str(e)}")
        return None

#Retrieval
def create_faiss_index(embeddings):
    if embeddings is None or len(embeddings) == 0:
        raise ValueError("لا توجد تضمينات صالحة")

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index

def semantic_search(query, index, chunks, top_k=3):
    """البحث عن الأجزاء الأكثر صلة"""
    query_emb = get_embeddings([query])
    if query_emb is None:
        return []

    distances, indices = index.search(query_emb, top_k)
    return [(chunks[i], float(distances[0][j])) for j, i in enumerate(indices[0])]

#LLM Integration
def generate_answer(question, context):
    """توليد الإجابة باستخدام Gemini"""
    prompt = f"""كن مساعدًا قانونيًا خبيرًا. اتبع القواعد:
    1. أجب بالعربية الفصحى فقط
    2. استخدم المعلومات التالية فقط:
    {context}
    3. إذا لا يوجد معلومات كافية قل "لا معلومات متاحة"

    السؤال: {question}
    الإجابة:"""

    try:
        response = gemini.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"خطأ في توليد الإجابة: {str(e)}"

# Initialize the index and chunks globally
pdf_path = "document.pdf"
pages = read_pdf(pdf_path)
chunks = semantic_chunking(pages)
embeddings = get_embeddings(chunks)
index = create_faiss_index(embeddings)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Arabic Legal Chatbot API",
        "docs": "/docs",
        "status": "operational"
    }

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        results = semantic_search(request.query, index, chunks)
        if not results:
            raise HTTPException(status_code=404, detail="No results found")

        context = "\n".join([c for c, _ in results])
        answer = generate_answer(request.query, context)

        sources = [
            {
                "content": chunk[:250] + ("..." if len(chunk) > 250 else ""),
                "similarity": float(1/(1+score))
            }
            for chunk, score in results
        ]

        return QueryResponse(answer=answer, sources=sources)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
