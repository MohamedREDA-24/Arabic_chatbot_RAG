import faiss
import numpy as np
import PyPDF2
import re
import google.generativeai as genai
import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
from datetime import datetime
from Agent import agent_executor
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

class FeedbackRequest(BaseModel):
    query: str
    answer: str
    feedback: bool  # True for thumbs up, False for thumbs down
    comment: Optional[str] = None

# Create feedback storage directory if it doesn't exist
FEEDBACK_DIR = "feedback_data"
if not os.path.exists(FEEDBACK_DIR):
    os.makedirs(FEEDBACK_DIR)

def save_feedback(feedback: FeedbackRequest):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    feedback_file = os.path.join(FEEDBACK_DIR, f"feedback_{timestamp}.json")
    
    feedback_data = {
        "query": feedback.query,
        "answer": feedback.answer,
        "feedback": feedback.feedback,
        "comment": feedback.comment,
        "timestamp": timestamp
    }
    
    with open(feedback_file, "w", encoding="utf-8") as f:
        json.dump(feedback_data, f, ensure_ascii=False, indent=2)

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
    query_emb = get_embeddings([query])
    if query_emb is None:
        return []
    distances, indices = index.search(query_emb, top_k)
    return [(chunks[i], float(distances[0][j])) for j, i in enumerate(indices[0])]

#LLM Integration
def generate_answer(question, context):
    prompt = f"""كن مساعدًا خبيرًا. اتبع القواعد:
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

# Feedback analysis and prompt improvement
def analyze_feedback():
    if not os.path.exists(FEEDBACK_DIR):
        return None
    
    feedback_files = [f for f in os.listdir(FEEDBACK_DIR) if f.endswith('.json')]
    negative_feedback = []
    
    for file in feedback_files:
        with open(os.path.join(FEEDBACK_DIR, file), 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not data['feedback']:  
                negative_feedback.append(data)
    
    return negative_feedback

def improve_prompt(question: str, context: str) -> str:
    negative_feedback = analyze_feedback()
    if not negative_feedback:
        return generate_answer(question, context)
    
    # Create a learning prompt based on negative feedback
    learning_context = "\n".join([
        f"السؤال: {fb['query']}\nالإجابة السابقة: {fb['answer']}\nالملاحظات: {fb['comment']}"
        for fb in negative_feedback[-5:]  # Use last 5 negative feedbacks
    ])
    
    improved_prompt = f"""كن مساعدًا خبيرًا. اتبع القواعد:
    1. أجب بالعربية الفصحى فقط
    2. استخدم المعلومات التالية فقط:
    {context}
    3. إذا لا يوجد معلومات كافية قل "لا معلومات متاحة"
    4. تعلم من الأخطاء السابقة:
    {learning_context}
    5. تأكد من أن إجابتك:
       - دقيقة ومباشرة
       - تستند إلى المعلومات المتاحة فقط
       - تتجنب الأخطاء السابقة المذكورة أعلاه

    السؤال: {question}
    الإجابة:"""

    try:
        response = gemini.generate_content(improved_prompt)
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
        answer = improve_prompt(request.query, context)  # Use improved prompt

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

@app.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    try:
        save_feedback(feedback)
        return {"status": "success", "message": "Feedback received successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




#agent 
@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        state = {"question": request.query}
        final_state = agent_executor.invoke(state)

        return QueryResponse(
            answer=final_state["answer"],
            sources=[],  # Optional: add chunk sources from search if needed
            follow_up=final_state.get("follow_up")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)