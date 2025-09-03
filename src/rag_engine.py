from src.embed_store import EmbedStore
from src.ollama_client import run_groq

class RAGChatbot:
    def __init__(self, json_path: str, model_name: str ="llama-3.3-70b-versatile"):
        self.store = EmbedStore()
        self.store.ensure_index(json_path)
        self.model_name = model_name
    
    def retrieve(self, query: str, k: int = 2) -> list[str]:
        return self.store.search(query, k)

    def ask(self, query: str, k: int = 2) -> str:
        retrieved = self.store.search(query, k)
        if not retrieved:
            return "No relevant employee data found."
    
        context_lines = []
        for idx, emp_text in enumerate(retrieved, start=1):
            context_lines.append(f"{idx}. {emp_text}")
    
        context = "\n".join(context_lines)
        prompt = (
    f"You are an HR assistant. Based on the following employee profiles and the query, "
    f"generate a professional HR-style recommendation.\n\n"
    f"Query: {query}\n\n"
    f"Employee Profiles:\n{context}\n\n"
    f"Response Guidelines:\n"
    f"- Begin with an introductory sentence explaining how many candidates were found.\n"
    f"- For each candidate:\n"
    f"   • State their name in bold.\n"
    f"   • Mention total years of experience.\n"
    f"   • Highlight their key projects related to the query.\n"
    f"   • List relevant technical skills.\n"
    f"   • Add details about availability or achievements (e.g., publications, certifications).\n"
    f"- End with a closing line offering to provide more details or arrange a meeting.\n\n"
    f"Write the response in a clear, human-readable style, similar to an HR recommendation email."
)


        try:
            return run_groq(prompt, self.model_name)
        except Exception as e:
            return f"Error generating answer: {str(e)}"
