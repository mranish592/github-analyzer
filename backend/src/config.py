import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN", "")