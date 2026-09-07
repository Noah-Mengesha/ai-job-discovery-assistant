import os, requests
RULES = """You are a truthful job application assistant. Use ONLY verified candidate facts.
Never invent skills, experience, dates, metrics, certifications, education, or accomplishments.
Distinguish missing requirements from verified qualifications. Do not claim an application was submitted.
Do not invent company-specific facts. If information is missing, flag it for human review."""
def generate(prompt):
    response=requests.post(os.getenv("OLLAMA_URL","http://localhost:11434/api/generate"),
        json={"model":os.getenv("OLLAMA_MODEL","llama3.1:8b"),"prompt":RULES+"\n\n"+prompt,"stream":False},
        timeout=180)
    response.raise_for_status()
    return response.json()["response"].strip()
