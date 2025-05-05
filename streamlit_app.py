import streamlit as st
import requests
import json
from typing import List, Dict

# Configure the page
st.set_page_config(
    page_title="المساعد العربي",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for RTL support and styling
st.markdown("""
    <style>
    .stApp {
        direction: rtl;
        text-align: right;
    }
    .stTextInput > div > div > input {
        text-align: right;
    }
    .chat-container {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 1rem;
        margin: 1rem 0;
    }
    .question {
        color: #2c3e50;
        font-size: 1.2rem;
        margin-bottom: 1rem;
    }
    .answer {
        color: #27ae60;
        font-size: 1.1rem;
        padding-right: 1rem;
        border-right: 3px solid #27ae60;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("المساعد العربي")
st.markdown("""
    مرحباً بك في المساعد العربي. يمكنك طرح أسئلتك وسيقوم النظام بالبحث في الوثائق وتقديم إجابات دقيقة.
""")

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Main chat interface
query = st.text_input("اكتب سؤالك هنا:", key="query_input")

if st.button("إرسال", key="send_button"):
    if query:
        try:
            # Call the FastAPI endpoint
            response = requests.post(
                "http://localhost:8000/query",
                json={"query": query}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Add to chat history
                st.session_state.chat_history.append({
                    "query": query,
                    "answer": result["answer"]
                })
            else:
                st.error("حدث خطأ في الاستجابة")
        except Exception as e:
            st.error("حدث خطأ في الاتصال")

# Display chat history
for chat in reversed(st.session_state.chat_history):
    st.markdown(f"""
        <div class="chat-container">
            <div class="question">السؤال: {chat['query']}</div>
            <div class="answer">الإجابة: {chat['answer']}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Add feedback buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("👍", key=f"thumbs_up_{chat['query']}"):
            try:
                feedback_data = {
                    "query": chat['query'],
                    "answer": chat['answer'],
                    "feedback": True,
                    "comment": None
                }
                response = requests.post(
                    "http://localhost:8000/feedback",
                    json=feedback_data
                )
                if response.status_code == 200:
                    st.success("شكراً على تقييمك الإيجابي!")
                else:
                    st.error("حدث خطأ في إرسال التقييم")
            except Exception as e:
                st.error("حدث خطأ في الاتصال")
    
    with col2:
        if st.button("👎", key=f"thumbs_down_{chat['query']}"):
            comment = st.text_input("يرجى كتابة ملاحظاتك لتحسين الإجابة:", key=f"comment_{chat['query']}")
            if comment:
                try:
                    feedback_data = {
                        "query": chat['query'],
                        "answer": chat['answer'],
                        "feedback": False,
                        "comment": comment
                    }
                    response = requests.post(
                        "http://localhost:8000/feedback",
                        json=feedback_data
                    )
                    if response.status_code == 200:
                        st.success("شكراً على ملاحظاتك! سنعمل على تحسين الإجابة.")
                    else:
                        st.error("حدث خطأ في إرسال التقييم")
                except Exception as e:
                    st.error("حدث خطأ في الاتصال") 