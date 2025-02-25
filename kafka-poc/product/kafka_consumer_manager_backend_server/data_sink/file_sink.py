# data_sinks/file_sink.py
import logging
import pandas as pd
from .base_sink import BaseDataSink

logger = logging.getLogger(__name__)

class FileSink(BaseDataSink):
    """
    A sink that writes DataFrames to a local file (e.g., CSV).
    """

    def __init__(self, file_path: str, mode: str = "append"):
        """
        :param file_path: path to the local file
        :param mode: "append" or "overwrite" or other logic
        """
        self.file_path = file_path
        self.mode = mode
        self._file_handle = None

    def connect(self):
        """
        For a file sink, 'connect' might open the file (if we want to keep it open).
        Or we can open/close it each time in `save_data`.
        """
        logger.info(f"FileSink connecting to {self.file_path} in mode={self.mode}")
        # If we want to open once and keep open:
        if self.mode == "overwrite":
            self._file_handle = open(self.file_path, "w", encoding="utf-8")
        else:
            self._file_handle = open(self.file_path, "a", encoding="utf-8")

    def save_data(self, df: pd.DataFrame):
        """
        Write the DataFrame as CSV lines into the file.
        """
        if not self._file_handle:
            raise RuntimeError("FileSink not connected. Call connect() first.")

        logger.debug(f"Writing {len(df)} rows to {self.file_path}")
        df.to_csv(self._file_handle, header=False, index=False)

        # If you prefer opening/closing for each write, do so here instead.
        # But then you'd move the opening logic from `connect` to `save_data`.

    def close(self):
        """
        Close the file handle if open.
        """
        if self._file_handle and not self._file_handle.closed:
            self._file_handle.close()
            logger.info(f"FileSink file {self.file_path} closed.")