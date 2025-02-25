# data_sinks/base_sink.py
import abc
import pandas as pd

class BaseDataSink(abc.ABC):
    """
    Abstract base class for different data sink adapters (RDBMS, NoSQL, local file, etc.).
    """

    @abc.abstractmethod
    def connect(self):
        """Establish or prepare the sink. Raises an exception if it fails."""
        pass

    @abc.abstractmethod
    def save_data(self, df: pd.DataFrame):
        """
        Save the given DataFrame to the sink (database, file, etc.).
        """
        pass

    @abc.abstractmethod
    def close(self):
        """Cleanly close any connections/resources."""
        pass