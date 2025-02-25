import json
import logging
import pandas as pd  # For example, if you want DataFrame support

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    A class responsible for transforming raw Kafka messages
    into a structured format (e.g., DataFrame).
    """

    def process_message(self, raw_msg: bytes) -> pd.DataFrame:
        """
        1) Convert the raw bytes into a string
        2) Parse JSON
        3) Convert to a pandas DataFrame
        (Adjust the logic as needed for your real business logic.)
        """
        try:
            msg_str = raw_msg.decode('utf-8')
            data = json.loads(msg_str)
            # Suppose each message is a list of records or a dict.
            # We'll handle a single record -> one-row DataFrame just as an example.
            if isinstance(data, dict):
                df = pd.DataFrame([data])
            elif isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                # fallback
                df = pd.DataFrame([{"unrecognized": data}])

            logger.debug(f"DataProcessor created DataFrame with shape={df.shape}")
            return df

        except Exception as e:
            logger.error(f"Failed to process message: {e}", exc_info=True)
            # You can re-raise or return None/empty df based on your design
            raise

    # Optionally, more specialized methods (e.g., DB insert, data cleansing) can go here.
