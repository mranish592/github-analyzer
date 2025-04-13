from src.app.main import app
import uvicorn
from src.utils.logging_util import logging_util

logger = logging_util.get_logger(__name__)
logger.info("Starting the application server")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)