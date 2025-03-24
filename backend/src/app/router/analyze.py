from fastapi import APIRouter
from pydantic import BaseModel, Field

from utils.github_util import github_util
class AnalyzeResponse(BaseModel):
    username: str = Field(..., title="Github username", description="The username of the github profile to analyze")
    name: str = Field(..., title="Name", description="The name of the github profile")
    message: str = Field(..., title="Message", description="Analysis of the github profile")
    repos: list = Field(..., title="Repositories", description="The repositories of the github profile")

router = APIRouter()

@router.get("/api/analyze/{username}")
async def analyze(username: str):
    """Fetches user data from the GitHub API."""
    user = github_util.get_user(username)
    repos = github_util.get_repositories_for_user(user)
    return AnalyzeResponse(
        username=username, 
        name=user.name, 
        repos=repos, 
        message=f"Hello, {username}!, you have {len(repos)} public repos"
    )