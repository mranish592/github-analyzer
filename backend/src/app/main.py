from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .router import root, analyze

app = FastAPI()
app.include_router(root.router)
app.include_router(analyze.router)

origins = [
    "http://localhost:5173",  # Allow requests from your React app (adjust port if needed)
    "http://localhost", #for local host
    "https://your-frontend-domain.com",  # Add your production frontend domain
    "https://your-api-domain.com", #allow api domain if different from frontend
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)