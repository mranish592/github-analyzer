import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GITHUB_REPO_BASE_URL = "https://github.com/"