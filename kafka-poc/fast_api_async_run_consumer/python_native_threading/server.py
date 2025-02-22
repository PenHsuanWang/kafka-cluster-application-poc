import uuid
import time
import logging
import threading
from typing import Dict

from fastapi import FastAPI, HTTPException
from kafka import KafkaConsumer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

app = FastAPI()


class ConsumerThread(threading.Thread):
    """
    A thread that continuously consumes messages from a Kafka topic
    and writes them to a file until asked to stop.
    """

    def __init__(self, broker: str, topic: str, file_path: str, group_id="demo-consumer-group"):
        super().__init__()
        self.broker = broker
        self.topic = topic
        self.file_path = file_path
        self.group_id = group_id
        self.stop_event = threading.Event()

    def run(self):
        """Main thread loop to consume Kafka messages."""
        logging.info(f"[{self.name}] Creating KafkaConsumer: broker={self.broker}, topic={self.topic}")
        try:
            consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=[self.broker],
                auto_offset_reset='earliest',  # or 'latest'
                enable_auto_commit=True,
                group_id=self.group_id
            )
        except Exception as e:
            logging.error(f"[{self.name}] Failed to create consumer: {e}", exc_info=True)
            return

        with open(self.file_path, 'a') as file:
            logging.info(f"[{self.name}] Starting consumption on topic={self.topic}")
            try:
                for message in consumer:
                    if self.stop_event.is_set():
                        logging.info(f"[{self.name}] Stop event received. Exiting loop.")
                        break

                    decoded_msg = message.value.decode('utf-8')
                    file.write(decoded_msg + "\n")
                    file.flush()
                    logging.info(f"[{self.name}] Consumed message: {decoded_msg}")
                    time.sleep(0.1)
            except Exception as e:
                logging.error(f"[{self.name}] Error while consuming messages: {e}", exc_info=True)
            finally:
                consumer.close()
                logging.info(f"[{self.name}] Consumer closed.")

    def stop(self):
        """Signal the thread to stop consuming and exit gracefully."""
        logging.info(f"[{self.name}] Stop signal received.")
        self.stop_event.set()


class ThreadManager:
    """
    Manages multiple Kafka consumer threads.
    Allows starting, stopping, and graceful shutdown with error handling.
    """
    def __init__(self):
        self._threads: Dict[str, ConsumerThread] = {}

    def start_consumer(self, broker: str, topic: str, file_path: str) -> str:
        """Creates and starts a new consumer thread, returning a unique ID."""
        consumer_id = str(uuid.uuid4())
        thread = ConsumerThread(broker, topic, file_path)
        self._threads[consumer_id] = thread
        thread.start()
        logging.info(f"[Manager] Started consumer {consumer_id} for topic={topic}")
        return consumer_id

    def stop_consumer(self, consumer_id: str):
        """Signals the consumer thread to stop, then joins it."""
        thread = self._threads.get(consumer_id)
        if not thread:
            raise ValueError(f"No consumer found with ID={consumer_id}")

        thread.stop()
        thread.join(timeout=10)  # Wait up to 10s for graceful exit
        if thread.is_alive():
            logging.warning(f"[Manager] Consumer {consumer_id} did not exit in time.")
        else:
            logging.info(f"[Manager] Consumer {consumer_id} stopped gracefully.")

        self._threads.pop(consumer_id, None)

    def stop_all(self):
        """Stops and joins all running threads."""
        for consumer_id in list(self._threads.keys()):
            try:
                self.stop_consumer(consumer_id)
            except ValueError:
                pass  # already stopped or missing

    def list_consumers(self) -> Dict[str, bool]:
        """Return the list of active consumers and their alive status."""
        return {cid: thr.is_alive() for cid, thr in self._threads.items()}

    def consumer_status(self, consumer_id: str) -> bool:
        """Return whether a specific consumer is alive."""
        thread = self._threads.get(consumer_id)
        if not thread:
            raise ValueError(f"No consumer found with ID={consumer_id}")
        return thread.is_alive()


# Create a global manager instance (in a real app, you might use a dependency)
manager = ThreadManager()


@app.post("/start-consumer")
def start_consumer(broker: str, topic: str, file_path: str):
    """
    Start a new Kafka consumer thread. Returns a unique consumer_id.
    """
    consumer_id = manager.start_consumer(broker, topic, file_path)
    return {
        "message": "Kafka consumer thread started",
        "consumer_id": consumer_id
    }


@app.post("/stop-consumer/{consumer_id}")
def stop_consumer(consumer_id: str):
    """
    Stop the specified Kafka consumer thread.
    """
    try:
        manager.stop_consumer(consumer_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"message": f"Consumer {consumer_id} stopped"}


@app.post("/stop-all")
def stop_all():
    """
    Stop all running Kafka consumer threads.
    """
    manager.stop_all()
    return {"message": "All consumers stopped"}


@app.get("/list-consumers")
def list_consumers():
    """
    List all active consumers and their alive status.
    """
    return manager.list_consumers()


@app.get("/consumer-status/{consumer_id}")
def consumer_status(consumer_id: str):
    """
    Check if a specific consumer thread is alive.
    """
    try:
        alive = manager.consumer_status(consumer_id)
        return {"consumer_id": consumer_id, "is_alive": alive}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)