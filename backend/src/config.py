import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GITHUB_REPO_BASE_URL = "https://github.com/"
    SONARQUBE_URL = os.getenv("SONARQUBE_URL", "")
    SONARQUBE_TOKEN = os.getenv("SONARQUBE_TOKEN", "")
    SONARQUBE_USER_TOKEN = os.getenv("SONARQUBE_USER_TOKEN", "")
    BASE_DIR = os.getenv("BASE_DIR", "/Users/anish/projects/github-analyzer/backend/local_repo_dir/base")