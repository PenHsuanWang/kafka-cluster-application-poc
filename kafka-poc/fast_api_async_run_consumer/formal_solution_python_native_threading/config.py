import logging

# Configure logging
LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

# In production, you might load environment variables here:
# import os
# BROKER_URL = os.getenv("KAFKA_BROKER_URL", "localhost:9092")
#
# Or use Pydantic for robust config handling.
