from .db import MongoDB
from config import Config

# Create a singleton instance
db = MongoDB(Config.MONGO_CONNECTION_STRING, Config.MONGO_DB_NAME)

# Export the instance
__all__ = ["db"] 