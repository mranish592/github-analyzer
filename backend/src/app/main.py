from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.logging_util import logging_util

from .router import root, analyze

logger = logging_util.get_logger(__name__)

app = FastAPI()
app.include_router(root.router)
app.include_router(analyze.router)

origins = ["*"]  # Allow requests from all origins

logger.info("Configuring CORS middleware")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)