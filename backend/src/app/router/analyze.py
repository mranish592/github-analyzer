from fastapi import APIRouter
from pydantic import BaseModel, Field
import httpx

class AnalyzeResponse(BaseModel):
    username: str = Field(..., title="Github username", description="The username of the github profile to analyze")
    message: str = Field(..., title="Message", description="Analysis of the github profile")

router = APIRouter()

@router.get("/api/analyze/{username}")
async def root(username: str):
    """Fetches user data from the GitHub API."""
    user_data = await get_github_user(username)
    print(user_data)
    return AnalyzeResponse(username=username, message=f"Hello, {username}!, you have {user_data['public_repos']} public repos")

async def get_github_user(username: str) -> dict | None:
    url = f"https://api.github.com/users/{username}"
    headers = {"Accept": "application/vnd.github+json"} #important for the newest github API.
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers = headers)
            print(response)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except httpx.HTTPError as exc:
            print(f"Error fetching GitHub user: {exc}")
            return None
        except httpx.RequestError as exc:
            print(f"Error making request: {exc}")
            return None