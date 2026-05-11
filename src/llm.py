
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
load_dotenv()
def get_llm():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise ValueError("GROQ_API_KEY not found in .env")
    return ChatGroq(
        groq_api_key=key,
        model_name=os.getenv("MODEL_NAME", "llama-3.3-70b-versatile"),
        temperature=0.2
    )
