import logging
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from consumers.manager import ThreadManager

logger = logging.getLogger(__name__)


# Request model to create a consumer
class CreateConsumerRequest(BaseModel):
    name: str
    broker: str
    topic: str
    file_path: str
    group_id: Optional[str] = "demo-consumer-group"
    auto_start: bool = True


# Request model to identify a consumer by ID
class ConsumerControlRequest(BaseModel):
    consumer_id: str


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = ThreadManager()


@app.post("/create-consumer")
def create_consumer(req: CreateConsumerRequest):
    """
    Create a new consumer record. If auto_start=True, it starts immediately (RUNNING).
    Otherwise, it remains CREATED until you call /start-consumer.
    If the Kafka broker is unreachable, an exception from manager.create_consumer
    will bubble up. We catch it here and return an HTTP 400 error.
    """
    try:
        consumer_id = manager.create_consumer(
            consumer_name=req.name,
            broker=req.broker,
            topic=req.topic,
            file_path=req.file_path,
            group_id=req.group_id or "demo-consumer-group",
            auto_start=req.auto_start
        )
        return {
            "message": "Consumer created",
            "consumer_id": consumer_id,
            "consumer_name": req.name,
            "auto_start": req.auto_start
        }
    except Exception as e:
        # We can log the error and raise HTTP 400 or 500, depending on your preference
        logger.error(f"Failed to create consumer: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/start-consumer")
def start_consumer(control: ConsumerControlRequest):
    """
    Start or resume the consumer with the given ID (status -> RUNNING).
    """
    success = manager.start_consumer(control.consumer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cannot start consumer.")
    return {"message": f"Consumer {control.consumer_id} started/resumed."}


@app.post("/pause-consumer")
def pause_consumer(control: ConsumerControlRequest):
    """
    Pause a RUNNING consumer (status -> PAUSED).
    """
    success = manager.pause_consumer(control.consumer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cannot pause consumer.")
    return {"message": f"Consumer {control.consumer_id} paused."}


@app.post("/terminate-consumer")
def terminate_consumer(control: ConsumerControlRequest):
    """
    Fully stop the consumer and remove it (status -> TERMINATED).
    """
    success = manager.terminate_consumer(control.consumer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cannot terminate consumer.")
    return {"message": f"Consumer {control.consumer_id} terminated."}


@app.get("/list-consumers")
def list_consumers():
    """
    Return metadata about all consumers.
    """
    return manager.list_consumers()


@app.get("/monitor-threads")
def monitor_threads():
    """
    Return a summary of all active threads (including system threads),
    and whether each one is recognized in the manager.
    """
    return manager.monitor_threads()


@app.on_event("shutdown")
def shutdown_event():
    logger.info("Shutting down. Terminating all consumers.")
    manager.stop_all()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
