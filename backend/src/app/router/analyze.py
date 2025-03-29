import asyncio
from fastapi import APIRouter
from pydantic import BaseModel, Field

from services.scoring_engine import scoring_engine
from services.extract_metrics import extract_metrics
from services.identify_skills import identify_skills
from services.ingestion import ingestion

router = APIRouter()

@router.get("/api/analyze/{username}")
async def analyze(username: str):
    """Fetches user data from the GitHub API."""
    user = await ingestion.ingest(username)
    user = await identify_skills.identify(user)
    user = await extract_metrics.extract(user)
    response = await scoring_engine.score(user)
    return response