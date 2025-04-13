from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .router import root, analyze

app = FastAPI()
app.include_router(root.router)
app.include_router(analyze.router)

origins = ["*"]  # Allow requests from all origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)