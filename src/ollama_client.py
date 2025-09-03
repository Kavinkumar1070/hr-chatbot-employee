import subprocess
import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def run_groq(prompt: str, model_name: str = "llama-3.3-70b-versatile") -> str:
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=512,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise RuntimeError(f"Groq API error: {str(e)}")


# def run_ollama(prompt: str, model_name: str = "llama3") -> str:
#     try:
#         result = subprocess.run(
#             ["ollama", "run", model_name],
#             input=prompt,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True,
#             encoding="utf-8"
#         )
#         if result.returncode != 0:
#             raise RuntimeError(f"Ollama error: {result.stderr.strip()}")
#         return result.stdout.strip()
#     except subprocess.TimeoutExpired:
#         raise RuntimeError("Ollama request timed out")
#     except Exception as e:
#         raise RuntimeError(f"Failed to run Ollama: {str(e)}")
