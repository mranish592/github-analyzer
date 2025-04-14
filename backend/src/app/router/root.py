from fastapi import APIRouter
from utils.logging_util import logging_util

logger = logging_util.get_logger(__name__)
router = APIRouter()

@router.get("/")
def root():
    logger.info("Root endpoint accessed")
    return {"message": "Hello, World!"}