from src.embed_store import EmbedStore
from src.ollama_client import run_groq

class RAGChatbot:
    def __init__(self, json_path: str, model_name: str ="llama-3.3-70b-versatile"):
        self.store = EmbedStore()
        self.store.ensure_index(json_path)
        self.model_name = model_name

    def ask(self, query: str, k: int = 3) -> str:
        retrieved = self.store.search(query, k)
        if not retrieved:
            return "No relevant employee data found."
    
        context_lines = []
        for idx, emp_text in enumerate(retrieved, start=1):
            context_lines.append(f"{idx}. {emp_text}")
    
        context = "\n".join(context_lines)
        prompt = (
            f"You are an HR assistant. Based on the following employee profiles and the query, "
            f"generate a detailed recommendation.\n\n"
            f"Query: {query}\n\n"
            f"Employee Profiles:\n{context}\n\n"
            f"Generate a human-readable answer explaining why each employee is suitable, "
            f"highlighting relevant experience, skills, projects, and availability."
        )
    
        try:
            return run_groq(prompt, self.model_name)
        except Exception as e:
            return f"Error generating answer: {str(e)}"
