"""
WSGI entry point for production deployment
"""
import logging
import sys

# Configure logging for WSGI with immediate flush
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

logger.info("WSGI: Starting application import...")

# Import the app (this will trigger API key initialization)
from index import app

logger.info("WSGI: Application import complete")

if __name__ == "__main__":
    app.run()