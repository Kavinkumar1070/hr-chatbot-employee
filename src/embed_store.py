import json
from pathlib import Path
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

class EmbedStore:
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        index_path: str = "data/employee_index.faiss",
        docs_path: str = "data/employee_docs.npy",
    ):
        self.embedder = SentenceTransformer(model_name)
        self.index = None
        self.docs = []
        self.index_path = Path(index_path)
        self.docs_path = Path(docs_path)

    def load_data(self, json_path: str):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        docs = []
        for emp in data.get("employees", []):
            text = (
                f"{emp['name']} with {emp['experience_years']} years experience. "
                f"Skills: {', '.join(emp.get('skills', []))}. "
                f"Projects: {', '.join(emp.get('past_projects', []))}. "
                f"Availability: {emp.get('availability', '')}."
            )
            docs.append(text)
        self.docs = docs
        return self.docs

    def build_index(self, docs: list = None):
        if docs is None:
            docs = self.docs

        if not docs:
            raise ValueError("No documents to build index.")

        embeddings = self.embedder.encode(docs, convert_to_numpy=True)
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)
        self.docs = docs

    def save(self):
        if self.index is None:
            raise ValueError("No index to save.")
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.index_path))
        np.save(self.docs_path, np.array(self.docs, dtype=object))

    def load(self):
        if not self.index_path.exists() or not self.docs_path.exists():
            raise FileNotFoundError("Index or docs not found.")
        self.index = faiss.read_index(str(self.index_path))
        self.docs = np.load(self.docs_path, allow_pickle=True).tolist()

    def ensure_index(self, json_path: str):
        if self.index_path.exists() and self.docs_path.exists():
            try:
                self.load()
                return
            except Exception:
                pass
        self.load_data(json_path)
        self.build_index()
        self.save()

    def search(self, query: str, k: int = 2):
        if self.index is None:
            raise ValueError("Index not loaded.")
        q_emb = self.embedder.encode([query], convert_to_numpy=True)
        D, I = self.index.search(q_emb, k)
        return [self.docs[i] for i in I[0]]
