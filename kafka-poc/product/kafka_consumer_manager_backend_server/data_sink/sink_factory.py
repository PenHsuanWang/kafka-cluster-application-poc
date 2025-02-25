# data_sinks/sink_factory.py
from typing import Dict
import logging
from .base_sink import BaseDataSink
from .mysql_sink import MySQLSink
from .mongo_sink import MongoSink
from .file_sink import FileSink

logger = logging.getLogger(__name__)

def create_sink(config: Dict) -> BaseDataSink:
    """
    Factory that returns a concrete DataSink adapter based on config["type"].
    """
    sink_type = config["type"].lower()

    if sink_type == "mysql":
        return MySQLSink(
            host=config["host"],
            user=config["user"],
            password=config["password"],
            database=config["database"],
            table_name=config["table_name"]
        )
    elif sink_type == "mongo":
        return MongoSink(
            uri=config["uri"],
            database=config["database"],
            collection=config["collection"]
        )
    elif sink_type == "file":
        file_path = config["file_path"]
        mode = config.get("mode", "append")  # default to append
        return FileSink(file_path=file_path, mode=mode)
    else:
        raise ValueError(f"Unsupported sink type: {sink_type}")