from fast_api_async_run_consumer.celery_task_queue.celery_app import celery_app
from kafka import KafkaConsumer
import time

@celery_app.task(bind=True, max_retries=5, default_retry_delay=10)
def kafka_consumer_task(self, broker: str, topic: str, file_path: str):
    """
    Connects to the Kafka broker, consumes messages from the given topic,
    and writes them continuously to a local file. Automatically retries on error.
    """
    try:
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=[broker],
            auto_offset_reset='earliest',  # or 'latest' as needed
            enable_auto_commit=True,
            group_id='demo-consumer-group'
        )

        with open(file_path, 'a') as file:
            print(f"Starting consumer for topic: {topic} from broker: {broker}")
            for message in consumer:
                decoded_msg = message.value.decode('utf-8')
                file.write(decoded_msg + "\n")
                file.flush()
                print(f"Consumed message: {decoded_msg}")
                time.sleep(0.1)
    except Exception as exc:
        print(f"Exception in Kafka consumer task: {exc}")
        # Automatically retry the task in case of error
        raise self.retry(exc=exc)