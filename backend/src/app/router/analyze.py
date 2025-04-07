import asyncio
from fastapi import APIRouter
from pydantic import BaseModel, Field

from utils.github_util import github_util
from core.models import AnalyzeResponse
from services.analysis_service import analysis_service
router = APIRouter()

@router.get("/api/analyze/{username}")
async def analyze(username: str) -> AnalyzeResponse:
    """Fetches user data from the GitHub API."""
    user = github_util.get_user(username)
    name = user.name
    experience_metrics, quality_metrics = analysis_service.analyze(username)
    response = AnalyzeResponse(username=username, name=name, message="Analyzed user", experience_metrics=experience_metrics, quality_metrics=quality_metrics)
    return response

