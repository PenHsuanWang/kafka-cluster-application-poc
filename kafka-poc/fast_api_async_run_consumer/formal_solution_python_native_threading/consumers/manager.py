import uuid
import logging
from typing import Dict, Optional

from .consumer_thread import ConsumerThread

logger = logging.getLogger(__name__)

class ThreadManager:
    """
    Manages multiple Kafka consumer threads.
    Allows starting, stopping, and graceful shutdown with error handling.
    """

    def __init__(self):
        # Map consumer_id -> (thread, client_id)
        self._threads: Dict[str, (ConsumerThread, Optional[str])] = {}

    def start_consumer(
        self,
        broker: str,
        topic: str,
        file_path: str,
        group_id: str = "demo-consumer-group",
        client_id: Optional[str] = None
    ) -> str:
        """Creates and starts a new consumer thread, returning a unique ID."""
        consumer_id = str(uuid.uuid4())
        thread = ConsumerThread(
            broker=broker,
            topic=topic,
            file_path=file_path,
            group_id=group_id,
            client_id=client_id
        )
        self._threads[consumer_id] = (thread, client_id)
        thread.start()
        logger.info(f"[Manager] Started consumer {consumer_id} for topic={topic} (client_id={client_id})")
        return consumer_id

    def stop_consumer(self, consumer_id: str):
        """Signals the consumer thread to stop, then joins it."""
        entry = self._threads.get(consumer_id)
        if not entry:
            raise ValueError(f"No consumer found with ID={consumer_id}")

        (thread, _) = entry
        thread.stop()
        thread.join(timeout=10)  # Wait up to 10s for graceful exit

        if thread.is_alive():
            logger.warning(f"[Manager] Consumer {consumer_id} did not exit in time.")
        else:
            logger.info(f"[Manager] Consumer {consumer_id} stopped gracefully.")

        self._threads.pop(consumer_id, None)

    def stop_all(self):
        """Stops and joins all running threads."""
        for consumer_id in list(self._threads.keys()):
            try:
                self.stop_consumer(consumer_id)
            except ValueError:
                pass

    def list_consumers(self):
        """
        Return a dict of consumer_id -> {
            "is_alive": bool,
            "client_id": str or None
        }
        """
        info = {}
        for cid, (thr, client_id) in self._threads.items():
            info[cid] = {
                "is_alive": thr.is_alive(),
                "client_id": client_id or thr.name,
            }
        return info

    def consumer_status(self, consumer_id: str):
        """Return the alive status and client_id of a specific consumer."""
        entry = self._threads.get(consumer_id)
        if not entry:
            raise ValueError(f"No consumer found with ID={consumer_id}")
        (thr, client_id) = entry
        return {
            "is_alive": thr.is_alive(),
            "client_id": client_id or thr.name
        }