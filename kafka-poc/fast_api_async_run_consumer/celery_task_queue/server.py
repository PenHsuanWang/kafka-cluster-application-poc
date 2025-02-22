from fastapi import FastAPI
from fast_api_async_run_consumer.celery_task_queue.kafka_consumer_task import kafka_consumer_task

app = FastAPI()

@app.post("/start-consumer")
async def start_consumer(broker: str, topic: str, file_path: str):
    """
    API endpoint to start the Kafka consumer as a Celery task.
    Returns the Celery task ID so that its status can be monitored.
    """
    task = kafka_consumer_task.delay(broker, topic, file_path)
    return {"message": "Kafka consumer task submitted", "task_id": task.id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)