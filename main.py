from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List
from fastapi.concurrency import run_in_threadpool
from src.rag_engine import RAGChatbot
import json
import logging

import math

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_groq import ChatGroq
from langchain.embeddings import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="HR Resource Query Chatbot")

chatbot = RAGChatbot("data/employees.json", model_name="llama-3.3-70b-versatile")

with open("data/employees.json", "r", encoding="utf-8") as f:
    data = json.load(f)
employees = data.get("employees", [])

with open("data/ground_truths.json", "r", encoding="utf-8") as f:
    ground_truths = json.load(f)

def get_ground_truth(query: str):
    for item in ground_truths:
        if item["query"].lower().strip() == query.lower().strip():
            return item["ground_truth"]  
    return None

class QueryRequest(BaseModel):
    query: str

@app.post("/chat")
async def chat_bot(request: QueryRequest):
    try:
        answer = await run_in_threadpool(lambda: chatbot.ask(request.query))
        return {"query": request.query, "answer": answer}
    except Exception as e:
        logger.error(f"Chatbot error: {str(e)}")
        return {"query": request.query, "error": str(e)}

def filter_employees(
    skills: List[str] = None,
    min_experience: int = 0,
    projects: List[str] = None,
    availability: str = None
    ):
    results = []
    for emp in employees:
        match = True

        if skills:
            emp_skills = [s.lower() for s in emp.get("skills", [])]
            if not all(skill.lower() in emp_skills for skill in skills):
                match = False

        if emp.get("experience_years", 0) < min_experience:
            match = False

        if projects:
            emp_projects = [p.lower() for p in emp.get("past_projects", [])]
            if not any(proj.lower() in emp_proj for proj in projects for emp_proj in emp_projects):
                match = False

        if availability and emp.get("availability", "").lower() != availability.lower():
            match = False

        if match:
            results.append(emp)

    return results

@app.get("/employees/search")
async def search_employees(
    skills: str = Query(None, description="Comma-separated skills, e.g. Python,AWS"),
    min_experience: int = Query(0, ge=0, description="Minimum years of experience"),
    projects: str = Query(None, description="Comma-separated project keywords"),
    availability: str = Query(None, description="Availability status")
):
    skills_list = [s.strip() for s in skills.split(",")] if skills else None
    projects_list = [p.strip() for p in projects.split(",")] if projects else None

    try:
        matched = filter_employees(skills_list, min_experience, projects_list, availability)
        return {"count": len(matched), "employees": matched}
    except Exception as e:
        logger.error(f"Employee search error: {str(e)}")
        return {"count": 0, "employees": [], "error": str(e)}



# def sanitize_nan(d):
#     if isinstance(d, dict):
#         return {k: sanitize_nan(v) for k, v in d.items()}
#     elif isinstance(d, list):
#         return [sanitize_nan(v) for v in d]
#     elif isinstance(d, float) and math.isnan(d):
#         return None
#     else:
#         return d

# @app.post("/evaluate")
# async def evaluate_query(request: QueryRequest):
#     try:
#         answer = await run_in_threadpool(lambda: chatbot.ask(request.query))

#         contexts = chatbot.retrieve(request.query)

#         ground_truth = get_ground_truth(request.query)
#         if not ground_truth:
#             return {
#                 "query": request.query,
#                 "answer": answer,
#                 "error": "No ground truth found for this query"
#             }

#         eval_data = {
#             "question": [request.query],
#             "answer": [answer],
#             "contexts": [contexts],
#             "reference": [ground_truth],
#         }
#         dataset = Dataset.from_dict(eval_data)

#         groq_llm = ChatGroq(model="llama-3.3-70b-versatile")
#         embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

#         evaluator_llm = LangchainLLMWrapper(groq_llm)
#         emd_wrap = LangchainEmbeddingsWrapper(embedding_model)

#         result = evaluate(
#             dataset,
#             metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
#             llm=evaluator_llm,
#             embeddings=emd_wrap
#         )

#         evaluation_dict = result.to_pandas().fillna(0).to_dict(orient="records")[0]

#         return {
#             "query": request.query,
#             "answer": answer,
#             "ground_truth": ground_truth,
#             "evaluation": evaluation_dict,
#         }
#     except Exception as e:
#         logger.error(f"Evaluation error: {str(e)}")
#         return {"query": request.query, "error": str(e)}
