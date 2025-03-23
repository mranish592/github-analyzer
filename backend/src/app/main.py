from fastapi import FastAPI

from .router import root

app = FastAPI()
app.include_router(root.router)