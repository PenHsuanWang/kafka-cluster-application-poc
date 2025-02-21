## Explanation

- **Kafka Consumer Task:**  
  The function `kafka_consumer_task` creates a `KafkaConsumer` for a given topic and broker. It continuously iterates over incoming messages, decodes each message, writes it to the specified file, and flushes the file to ensure that data is written immediately.

- **FastAPI Endpoint:**  
  The `/start-consumer` endpoint accepts `broker`, `topic`, and `file_path` as query parameters. It uses FastAPI’s `BackgroundTasks` to run the Kafka consumer task asynchronously in the background, allowing the API to return immediately.

- **Running the Server:**  
  The script uses `uvicorn` to run the FastAPI server on host `0.0.0.0` and port `8000`. You can call the endpoint (e.g., via HTTP POST) to start the consumer.

This example is intended for demonstration and may need enhancements (like error handling and graceful shutdown) for production use.