from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict

# Import your Kafka consumer manager
from consumers.manager import ThreadManager

app = FastAPI()
manager = ThreadManager()


# Request Models
class StartConsumerRequest(BaseModel):
    broker: str = Field(..., example="localhost:9092", description="Kafka broker address")
    topic: str = Field(..., example="my_topic", description="Kafka topic to consume from")
    file_path: str = Field(..., example="/path/to/logfile.log",
                           description="Local file path to write consumed messages")
    group_id: Optional[str] = Field(
        "demo-consumer-group",
        example="demo-consumer-group",
        description="Kafka consumer group ID"
    )
    client_id: Optional[str] = Field(
        None,
        example="my_client",
        description="Optional custom client ID for the consumer"
    )


# Response Models
class StartConsumerResponse(BaseModel):
    message: str
    consumer_id: str
    client_id: Optional[str]
    group_id: str


class StopConsumerResponse(BaseModel):
    message: str


class StopAllResponse(BaseModel):
    message: str


class ConsumerStatusResponse(BaseModel):
    is_alive: bool
    client_id: str


# Endpoints using Pydantic models for input validation and output structure.

@app.post("/start-consumer", response_model=StartConsumerResponse)
def start_consumer(request: StartConsumerRequest):
    """
    Start a new Kafka consumer thread.

    This endpoint accepts a JSON body that is validated against StartConsumerRequest.
    If the data is invalid, FastAPI returns a 422 error with details.
    """
    try:
        consumer_id = manager.start_consumer(
            broker=request.broker,
            topic=request.topic,
            file_path=request.file_path,
            group_id=request.group_id,
            client_id=request.client_id
        )
        return {
            "message": "Kafka consumer thread started",
            "consumer_id": consumer_id,
            "client_id": request.client_id,
            "group_id": request.group_id
        }
    except Exception as e:
        # Generic error handling; you might refine this per your application's needs.
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/stop-consumer/{consumer_id}", response_model=StopConsumerResponse)
def stop_consumer(consumer_id: str):
    """
    Stop a specific Kafka consumer thread by its consumer_id.

    The consumer_id is validated as a path parameter.
    If the consumer is not found, a 404 error is returned.
    """
    try:
        manager.stop_consumer(consumer_id)
        return {"message": f"Consumer {consumer_id} stopped"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/stop-all", response_model=StopAllResponse)
def stop_all():
    """
    Stop all active Kafka consumer threads.
    """
    manager.stop_all()
    return {"message": "All consumers stopped"}


@app.get("/list-consumers", response_model=Dict[str, ConsumerStatusResponse])
def list_consumers():
    """
    List all active consumers.

    Returns a dictionary mapping consumer IDs to their status (is_alive) and client_id.
    """
    # manager.list_consumers() is expected to return a dict like:
    # {consumer_id: {"is_alive": bool, "client_id": str}, ...}
    return manager.list_consumers()


@app.get("/consumer-status/{consumer_id}", response_model=ConsumerStatusResponse)
def consumer_status(consumer_id: str):
    """
    Retrieve the status of a specific consumer thread.

    Returns whether the consumer is alive and its client identifier.
    """
    try:
        return manager.consumer_status(consumer_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.on_event("shutdown")
def shutdown_event():
    """
    Ensure that all consumer threads are stopped gracefully when the server shuts down.
    """
    manager.stop_all()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)