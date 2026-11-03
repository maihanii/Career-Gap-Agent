import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
model = os.getenv("OPENROUTER_MODEL")

if not api_key or not model:
    raise ValueError("OpenRouter API key or model is missing from .env")

llm = ChatOpenAI(
    model=model,
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
    temperature=0
)
