from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
import json, os
from RAG_Module import improve_prompt, analyze_feedback, semantic_search, get_embeddings, create_faiss_index, read_pdf, semantic_chunking

# Define state
class AgentState(TypedDict):
    question: str
    context: Optional[str]
    answer: Optional[str]
    feedback_notes: Optional[list[str]]
    follow_up: Optional[str]

# Nodes
def load_context(state: AgentState) -> AgentState:
    results = semantic_search(state["question"], index, chunks)
    context = "\n".join([c for c, _ in results])
    return {**state, "context": context}

def generate_answer_node(state: AgentState) -> AgentState:
    answer = improve_prompt(state["question"], state["context"])
    return {**state, "answer": answer}

def analyze_feedback_node(state: AgentState) -> AgentState:
    feedback = analyze_feedback()
    comments = [fb["comment"] for fb in feedback[-3:]] if feedback else []
    return {**state, "feedback_notes": comments}

def follow_up_question_node(state: AgentState) -> AgentState:
    if "لا معلومات متاحة" in state["answer"] or len(state["answer"].split()) < 30:
        follow_up = "هل ترغب في توضيح إضافي أو إعادة صياغة السؤال؟"
    else:
        follow_up = None
    return {**state, "follow_up": follow_up}

# Create Graph
graph = StateGraph(AgentState)

graph.add_node("load_context", load_context)
graph.add_node("analyze_feedback", analyze_feedback_node)
graph.add_node("generate_answer", generate_answer_node)
graph.add_node("generate_follow_up", follow_up_question_node)

graph.set_entry_point("load_context")
graph.add_edge("load_context", "analyze_feedback")
graph.add_edge("analyze_feedback", "generate_answer")
graph.add_edge("generate_answer", "generate_follow_up")
graph.add_edge("generate_follow_up", END)

agent_executor = graph.compile()
