import asyncio
from fastapi import APIRouter
from pydantic import BaseModel, Field

from utils.github_util import github_util
from core.models import AnalyzeResponse, StatusResponse, SubmitAnalysisResponse
from services.analysis_service import analysis_service
router = APIRouter()

@router.get("/api/analyze/{username}")
async def analyze(username: str, skip_quality_metrics: bool = False) -> AnalyzeResponse:
    """Fetches user data from the GitHub API."""
    user = github_util.get_user(username)
    name = user.name if user.name is not None else username
    experience_metrics, quality_metrics = analysis_service.analyze('', username, skip_quality_metrics)
    response = AnalyzeResponse(username=username, name=name, message="Analyzed user", experience_metrics=experience_metrics, quality_metrics=quality_metrics)
    return response


@router.post("/api/submit/{username}")
async def submit_analysis(username: str, skip_quality_metrics: bool = False) -> SubmitAnalysisResponse:
    analysis_id, name = analysis_service.submit_analysis(username, skip_quality_metrics)
    print('got analysis id for', username, 'with id', analysis_id)
    return SubmitAnalysisResponse(username=username, analysis_id=analysis_id, name=name)

@router.get("/api/status/{analysis_id}")
async def status(analysis_id: str) -> StatusResponse:
    status = analysis_service.get_status(analysis_id)
    return StatusResponse(analysis_id=analysis_id, status=status)

@router.get("/api/analysis/{analysis_id}")
async def get_analysis(analysis_id: str) -> AnalyzeResponse:
    analysis = analysis_service.get_analysis(analysis_id)
    username = analysis.username
    name = analysis.name    
    experience_metrics = analysis.experience_metrics
    quality_metrics = analysis.quality_metrics
    return AnalyzeResponse(username=username, name=name, message="Analysis completed", experience_metrics=experience_metrics, quality_metrics=quality_metrics)