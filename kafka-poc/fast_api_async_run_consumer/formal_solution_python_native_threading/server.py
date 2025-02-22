import logging
from typing import Optional

from fastapi import FastAPI, HTTPException, Query

# Import your config so it runs before everything else (e.g. logging config).
import config
from consumers.manager import ThreadManager

logger = logging.getLogger(__name__)

app = FastAPI()
manager = ThreadManager()

@app.post("/start-consumer")
def start_consumer(
    broker: str,
    topic: str,
    file_path: str,
    group_id: str = Query("demo-consumer-group", description="Kafka consumer group ID"),
    client_id: Optional[str] = Query(None, description="Optional friendly name for the consumer")
):
    """
    Start a new Kafka consumer thread. Returns a unique consumer_id.
    Optionally provide a 'client_id' to set a custom Kafka client_id & thread name.
    """
    consumer_id = manager.start_consumer(broker, topic, file_path, group_id, client_id)
    return {
        "message": "Kafka consumer thread started",
        "consumer_id": consumer_id,
        "client_id": client_id,
        "group_id": group_id
    }

@app.post("/stop-consumer/{consumer_id}")
def stop_consumer(consumer_id: str):
    """Stop the specified Kafka consumer thread."""
    try:
        manager.stop_consumer(consumer_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"message": f"Consumer {consumer_id} stopped"}

@app.post("/stop-all")
def stop_all():
    """Stop all running Kafka consumer threads."""
    manager.stop_all()
    return {"message": "All consumers stopped"}

@app.get("/list-consumers")
def list_consumers():
    """List all active consumers, their status, and client_id."""
    return manager.list_consumers()

@app.get("/consumer-status/{consumer_id}")
def consumer_status(consumer_id: str):
    """Check if a specific consumer thread is alive and see its client_id."""
    try:
        return manager.consumer_status(consumer_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Optional: Add graceful shutdown to ensure threads are stopped when server shuts down.
@app.on_event("shutdown")
def shutdown_event():
    logger.info("Shutting down. Stopping all consumer threads.")
    manager.stop_all()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)