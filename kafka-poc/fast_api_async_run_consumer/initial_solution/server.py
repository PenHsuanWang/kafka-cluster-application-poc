from fastapi import FastAPI, BackgroundTasks
from kafka import KafkaConsumer
import time

app = FastAPI()


def kafka_consumer_task(broker: str, topic: str, file_path: str):
    """
    Connect to the Kafka broker and subscribe to the given topic.
    Continuously consume messages and write them to a local file.
    """
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=[broker],
        auto_offset_reset='earliest',  # Change to 'latest' as needed
        enable_auto_commit=True,
        group_id='demo-consumer-group'
    )

    # Open the file in append mode
    with open(file_path, 'a') as file:
        print(f"Starting consumer for topic: {topic} from broker: {broker}")
        # The consumer loop
        for message in consumer:
            # Decode the message value (assuming UTF-8 encoding)
            decoded_msg = message.value.decode('utf-8')
            # Write the message to the file and flush to ensure it's written immediately
            file.write(decoded_msg + "\n")
            file.flush()
            # Optional: print to console for debugging/demo purposes
            print(f"Consumed message: {decoded_msg}")
            # You can add a sleep here if needed to throttle processing
            time.sleep(0.1)


@app.post("/start-consumer")
async def start_consumer(broker: str, topic: str, file_path: str, background_tasks: BackgroundTasks):
    """
    API endpoint to start the Kafka consumer in the background.
    You need to supply the broker address, topic name, and output file path.
    """
    # Add the consumer task to run in the background.
    background_tasks.add_task(kafka_consumer_task, broker, topic, file_path)
    return {"message": "Kafka consumer started in the background"}


if __name__ == "__main__":
    # Run the FastAPI app with uvicorn
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
