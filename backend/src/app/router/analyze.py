from fastapi import APIRouter
from pydantic import BaseModel, Field

from utils.github_util import github_util
from utils.gitingest_util import git_ingest_util
from utils.langchain_util import langchain_util

class AnalyzeResponse(BaseModel):
    username: str = Field(..., title="Github username", description="The username of the github profile to analyze")
    name: str = Field(..., title="Name", description="The name of the github profile")
    message: str = Field(..., title="Message", description="Analysis of the github profile")
    languages: list = Field(..., title="Languages", description="The languages of the github profile")
    frameworks: list = Field(..., title="Frameworks", description="The frameworks of the github profile")
    repos: list = Field(..., title="Repositories", description="The repositories of the github profile")

router = APIRouter()

@router.get("/api/analyze/{username}")
async def analyze(username: str):
    """Fetches user data from the GitHub API."""
    user = github_util.get_user(username)
    repos = github_util.get_repositories_for_user(user)
    all_languages = set()
    all_frameworks = set()
    for repo in repos:
        await git_ingest_util.get_file_structure(repo)
        languages, frameworks = await langchain_util.get_languages_and_frameworks(repo)
        all_languages.update(languages)
        all_frameworks.update(frameworks)
        print("Repo", repo, "languages", languages, "frameworks", frameworks)
    return AnalyzeResponse(
        username=username, 
        name=user.name, 
        repos=repos, 
        languages=list(all_languages),
        frameworks=list(all_frameworks),
        message=f"Hello, {username}!, you have {len(repos)} public repos"
    )