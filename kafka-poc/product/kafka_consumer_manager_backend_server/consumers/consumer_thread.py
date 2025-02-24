import time
import logging
import threading
from kafka import KafkaConsumer

logger = logging.getLogger(__name__)

class ConsumerThread(threading.Thread):
    """
    A thread that continuously consumes messages from a Kafka topic
    and writes them to a file, with support for pausing and stopping.
    Also uses init_done and init_error to propagate startup exceptions.
    """

    def __init__(
        self,
        broker: str,
        topic: str,
        file_path: str,
        group_id: str = "demo-consumer-group",
        client_id: str = None
    ):
        super().__init__(name=client_id or f"ConsumerThread-{id(self)}")

        self.broker = broker
        self.topic = topic
        self.file_path = file_path
        self.group_id = group_id
        self.client_id = client_id

        # Signals for pausing or fully stopping consumption
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()

        # For startup error propagation:
        self.init_done = threading.Event()
        self.init_error = None

    def run(self):
        logger.info(f"[{self.name}] Creating KafkaConsumer: broker={self.broker}, topic={self.topic}")
        try:
            consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=[self.broker],
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id=self.group_id,
                client_id=self.client_id or f"python-consumer-{id(self)}"
            )
            # If we got here, the consumer connected successfully
            self.init_done.set()
        except Exception as e:
            logger.error(f"[{self.name}] Failed to create consumer: {e}", exc_info=True)
            self.init_error = e
            # Signal main thread that startup failed
            self.init_done.set()
            return  # stop run() here

        # Normal consumption flow if init succeeded
        with open(self.file_path, 'a') as file:
            logger.info(f"[{self.name}] Starting consumption on topic={self.topic}")
            try:
                for message in consumer:
                    # Check if we are fully stopping
                    if self.stop_event.is_set():
                        logger.info(f"[{self.name}] Stop event set. Exiting consumer loop.")
                        break

                    # If paused, skip reading messages
                    if self.pause_event.is_set():
                        time.sleep(0.1)
                        continue

                    # Otherwise, process the message
                    decoded_msg = message.value.decode('utf-8')
                    file.write(decoded_msg + "\n")
                    file.flush()
                    logger.info(f"[{self.name}] Consumed message: {decoded_msg}")
                    time.sleep(0.1)
            except Exception as e:
                logger.error(f"[{self.name}] Error while consuming messages: {e}", exc_info=True)
            finally:
                consumer.close()
                logger.info(f"[{self.name}] Consumer closed.")

    def pause(self):
        """Pause consumption without killing the thread."""
        logger.info(f"[{self.name}] Pause signal received.")
        self.pause_event.set()

    def resume(self):
        """Resume consumption if paused."""
        logger.info(f"[{self.name}] Resume signal received.")
        self.pause_event.clear()

    def stop(self):
        """Fully stop the thread and exit."""
        logger.info(f"[{self.name}] Stop signal received.")
        self.stop_event.set()
        # Clear pause_event in case we are paused
        self.pause_event.clear()