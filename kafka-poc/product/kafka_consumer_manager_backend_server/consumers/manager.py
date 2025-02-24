import uuid
import logging
import threading
from typing import Dict, Any, List

from .consumer_thread import ConsumerThread

logger = logging.getLogger(__name__)

class ThreadManager:
    """
    Manages multiple Kafka consumer threads. Each consumer has a status:
      - CREATED
      - RUNNING
      - PAUSED
      - TERMINATED
    """

    def __init__(self):
        # Key: consumer_id (UUID string)
        # Value: dict with:
        #   "thread": ConsumerThread
        #   "name": str (user-friendly name)
        #   "broker": str
        #   "topic": str
        #   "file_path": str
        #   "group_id": str
        #   "status": str (CREATED, RUNNING, PAUSED, TERMINATED)
        self._consumers: Dict[str, Dict[str, Any]] = {}

    def create_consumer(
        self,
        consumer_name: str,
        broker: str,
        topic: str,
        file_path: str,
        group_id: str,
        auto_start: bool = True
    ) -> str:
        """
        Create a consumer record. If auto_start=True, we also start the thread.
        """
        consumer_id = str(uuid.uuid4())
        thread = ConsumerThread(
            broker=broker,
            topic=topic,
            file_path=file_path,
            group_id=group_id,
            client_id=consumer_name
        )

        record = {
            "thread": thread,
            "name": consumer_name,
            "broker": broker,
            "topic": topic,
            "file_path": file_path,
            "group_id": group_id,
            "status": "CREATED"
        }

        self._consumers[consumer_id] = record
        logger.info(f"Created consumer '{consumer_name}' (ID={consumer_id}), status=CREATED")

        if auto_start:
            self.start_consumer(consumer_id)

        return consumer_id

    def start_consumer(self, consumer_id: str) -> bool:
        """
        If status is CREATED or PAUSED, start/resume the thread. Status -> RUNNING.
        """
        record = self._consumers.get(consumer_id)
        if not record:
            return False

        status = record["status"]
        thread = record["thread"]

        if status == "TERMINATED":
            logger.warning(f"Cannot start consumer {consumer_id}, it is TERMINATED.")
            return False

        if status == "RUNNING":
            logger.info(f"Consumer '{record['name']}' (ID={consumer_id}) already RUNNING.")
            return True

        if status == "CREATED":
            # Actually start the thread
            thread.start()
            record["status"] = "RUNNING"
            logger.info(f"Started consumer '{record['name']}' (ID={consumer_id}).")
            return True

        if status == "PAUSED":
            # Resume
            thread.resume()
            record["status"] = "RUNNING"
            logger.info(f"Resumed consumer '{record['name']}' (ID={consumer_id}).")
            return True

        return False

    def pause_consumer(self, consumer_id: str) -> bool:
        """
        If RUNNING, pause the thread. Status -> PAUSED.
        """
        record = self._consumers.get(consumer_id)
        if not record:
            return False

        if record["status"] == "RUNNING":
            record["thread"].pause()
            record["status"] = "PAUSED"
            logger.info(f"Paused consumer '{record['name']}' (ID={consumer_id}).")
            return True

        logger.warning(f"Cannot pause consumer {consumer_id}, status={record['status']}.")
        return False

    def terminate_consumer(self, consumer_id: str) -> bool:
        """
        Fully stop the thread (if running/paused/created) and mark as TERMINATED.
        Remove it from the manager so it's no longer listed.
        """
        record = self._consumers.get(consumer_id)
        if not record:
            return False

        status = record["status"]
        thread = record["thread"]

        if status not in ["TERMINATED"]:
            # Stop the thread if it's not already gone
            thread.stop()
            thread.join(timeout=5)
            record["status"] = "TERMINATED"
            logger.info(f"Terminated consumer '{record['name']}' (ID={consumer_id}).")

        # Optionally remove from dictionary so we don't list it again
        del self._consumers[consumer_id]
        return True

    def stop_all(self):
        """
        Stop all RUNNING or PAUSED or CREATED consumers. Mark them TERMINATED.
        """
        for cid in list(self._consumers.keys()):
            self.terminate_consumer(cid)

    def get_consumer_by_id(self, consumer_id: str) -> Any:
        return self._build_consumer_dict(consumer_id, self._consumers.get(consumer_id))

    def list_consumers(self) -> List[Dict[str, Any]]:
        """
        Return a list of all consumers with metadata.
        """
        results = []
        for cid, record in self._consumers.items():
            results.append(self._build_consumer_dict(cid, record))
        return results

    def _build_consumer_dict(self, consumer_id: str, record: Dict[str, Any]) -> Dict[str, Any]:
        if not record:
            return {}
        return {
            "consumer_id": consumer_id,
            "consumer_name": record["name"],
            "broker": record["broker"],
            "topic": record["topic"],
            "file_path": record["file_path"],
            "group_id": record["group_id"],
            "status": record["status"]
        }

    def monitor_threads(self) -> List[Dict[str, Any]]:
        """
        Return a summary of all active threads in Python,
        plus a note about whether they're recognized in the manager.
        """
        active = threading.enumerate()  # list of Thread objects
        results = []

        # Convert your manager’s dict to a set of threads for quick lookup
        manager_threads = set(
            record["thread"] for record in self._consumers.values()
        )

        for th in active:
            # Check if it's one of your ConsumerThreads or a system thread
            is_consumer = (th in manager_threads)
            results.append({
                "thread_name": th.name,
                "is_consumer": is_consumer,
                "alive": th.is_alive()
            })

        return results