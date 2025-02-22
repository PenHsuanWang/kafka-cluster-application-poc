import time
import logging
import threading
from kafka import KafkaConsumer

logger = logging.getLogger(__name__)

class ConsumerThread(threading.Thread):
    """
    A thread that continuously consumes messages from a Kafka topic
    and writes them to a file until asked to stop.
    """

    def __init__(
        self,
        broker: str,
        topic: str,
        file_path: str,
        group_id: str = "demo-consumer-group",
        client_id: str = None
    ):
        """
        :param broker: Kafka broker (e.g. 'localhost:9092')
        :param topic: Kafka topic to consume
        :param file_path: Local file to write consumed messages
        :param group_id: Kafka consumer group ID
        :param client_id: Custom client ID for Kafka (and used as thread name if provided)
        """
        thread_name = client_id if client_id else f"ConsumerThread-{id(self)}"
        super().__init__(name=thread_name)

        self.broker = broker
        self.topic = topic
        self.file_path = file_path
        self.group_id = group_id
        self.client_id = client_id
        self.stop_event = threading.Event()

    def run(self):
        logger.info(f"[{self.name}] Creating KafkaConsumer: broker={self.broker}, topic={self.topic}")
        try:
            consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=[self.broker],
                auto_offset_reset='earliest',  # or 'latest' as needed
                enable_auto_commit=True,
                group_id=self.group_id,
                client_id=self.client_id or f"python-consumer-{id(self)}"
            )
        except Exception as e:
            logger.error(f"[{self.name}] Failed to create consumer: {e}", exc_info=True)
            return

        with open(self.file_path, 'a') as file:
            logger.info(f"[{self.name}] Starting consumption on topic={self.topic}")
            try:
                for message in consumer:
                    if self.stop_event.is_set():
                        logger.info(f"[{self.name}] Stop event received. Exiting loop.")
                        break

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

    def stop(self):
        logger.info(f"[{self.name}] Stop signal received.")
        self.stop_event.set()