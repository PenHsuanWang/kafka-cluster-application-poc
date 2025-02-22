# Kafka Consumer with Native Python Threading

This project demonstrates a **production-style** Python service using **native threading** to manage multiple Kafka consumers. Each consumer runs in its own thread, continuously reading messages from a Kafka topic and writing them to a local file. The application exposes a **FastAPI** interface, allowing you to start, stop, and list active consumers.

---

## Table of Contents

1. [Project Overview](#project-overview)  
2. [Folder Structure](#folder-structure)  
3. [Installation](#installation)  
4. [Configuration](#configuration)  
5. [Running the Application](#running-the-application)  
6. [API Endpoints](#api-endpoints)  
7. [Key Components](#key-components)  
8. [Parameters & Settings](#parameters--settings)  
9. [Scaling & Partitioning Notes](#scaling--partitioning-notes)  
10. [License](#license)

---

## Project Overview

- **Purpose**: Provide a simple, maintainable, and production-friendly way to consume Kafka messages using Python’s built-in **threading**.  
- **Key Features**:  
  - Each consumer runs in a separate thread (`ConsumerThread`), with graceful stop and error handling.  
  - A `ThreadManager` keeps track of all running consumers and handles start/stop actions.  
  - A **FastAPI** server exposes REST endpoints to manage the lifecycle of these consumer threads.

This approach is well-suited for **I/O-bound** workloads (e.g., reading from Kafka, writing to files). If you have CPU-intensive processing, consider **multiprocessing** or a task queue like **Celery**.

---

## Folder Structure

```plaintext
my_kafka_app/
├── consumers/
│   ├── __init__.py
│   ├── consumer_thread.py
│   └── manager.py
├── server.py
├── config.py
├── requirements.txt
├── README.md
└── pyproject.toml
```

| File/Folder               | Description                                                                                                          |
|---------------------------|----------------------------------------------------------------------------------------------------------------------|
| **consumers/**            | Holds consumer-related logic.                                                                                       |
| `consumer_thread.py`      | Defines the `ConsumerThread` class that continuously reads messages from Kafka.                                     |
| `manager.py`              | Defines the `ThreadManager` class, which starts/stops consumer threads and keeps track of them.                     |
| **server.py**             | The FastAPI entry point. Defines REST endpoints to start/stop/list consumers.                                       |
| **config.py**             | Contains logging or environment configuration. In production, you can extend this with more robust settings.        |
| **requirements.txt**      | Lists Python dependencies. Install via `pip install -r requirements.txt`.                                           |
| **README.md**             | This file, describing the project.                                                                                  |
| **pyproject.toml**        | (Optional) Modern packaging configuration. You could use a `setup.py` if you prefer setuptools.                     |

---

## Installation

**Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   This installs:
   - **FastAPI** for the web server and endpoints.
   - **uvicorn** as the ASGI server.
   - **kafka-python** for Kafka consumer functionality.


---

## Configuration

- **Logging** is configured in `config.py`. By default, it prints INFO-level logs to stdout.  
- **Kafka Broker** can be specified dynamically via the API (e.g., `broker=localhost:9092`).  
- **Consumer Group** can also be set dynamically. Defaults to `demo-consumer-group`.

For more complex setups (e.g., environment variables, secrets management), extend `config.py` or integrate a library like [Pydantic Settings](https://docs.pydantic.dev/latest/usage/pydantic_settings/).

---

## Running the Application

1. **Start the FastAPI server** (development):
   ```bash
   python server.py
   ```
   or using uvicorn directly:
   ```bash
   uvicorn server:app --host 0.0.0.0 --port 8000
   ```

2. **Access the OpenAPI docs**:
   - Open your browser to `http://localhost:8000/docs` to see interactive Swagger documentation.

---

## API Endpoints

| Endpoint                                       | Method | Description                                                                                                                          |
|------------------------------------------------|--------|--------------------------------------------------------------------------------------------------------------------------------------|
| **`/start-consumer`**                          | `POST` | Start a new Kafka consumer thread. Requires `broker`, `topic`, `file_path` as query parameters; optional `group_id` and `client_id`. |
| **`/stop-consumer/{consumer_id}`**             | `POST` | Stop a single consumer thread by its unique `consumer_id`.                                                                           |
| **`/stop-all`**                                | `POST` | Stop all running consumer threads.                                                                                                   |
| **`/list-consumers`**                          | `GET`  | Returns a JSON object of all active consumers, their alive status, and their client ID.                                              |
| **`/consumer-status/{consumer_id}`**           | `GET`  | Returns whether a specific consumer thread is alive, plus the client ID.                                                             |

### Example Usage

```bash
# 1. Start a consumer
curl -X POST "http://localhost:8000/start-consumer?broker=localhost:9092&topic=TopicA&file_path=./outputA.txt&group_id=demo-group&client_id=ConsumerA"

# 2. List active consumers
curl "http://localhost:8000/list-consumers"

# 3. Check a consumer's status
curl "http://localhost:8000/consumer-status/<consumer_id>"

# 4. Stop a specific consumer
curl -X POST "http://localhost:8000/stop-consumer/<consumer_id>"

# 5. Stop all consumers
curl -X POST "http://localhost:8000/stop-all"
```

---

## Key Components

1. **`ConsumerThread`** (in `consumer_thread.py`):
   - Inherits from `threading.Thread`.
   - Creates a `KafkaConsumer` in its `run()` method.
   - Polls messages in a loop until a `stop_event` is set.

2. **`ThreadManager`** (in `manager.py`):
   - Spawns and tracks multiple `ConsumerThread` instances.
   - Provides methods to start a consumer (`start_consumer`), stop a consumer (`stop_consumer`), stop all consumers (`stop_all`), and query status.

3. **`server.py`**:
   - FastAPI application exposing endpoints to interact with the `ThreadManager`.
   - Uses a global `manager = ThreadManager()` instance to handle requests.

4. **`config.py`**:
   - Sets up logging via `logging.basicConfig`.
   - In production, you can load environment variables, configure advanced logging, etc.

---

## Parameters & Settings

| Parameter   | Location   | Default                  | Description                                                                                                            |
|-------------|-----------|--------------------------|------------------------------------------------------------------------------------------------------------------------|
| `broker`    | Query      | *(required)*             | The Kafka broker address, e.g. `localhost:9092`.                                                                       |
| `topic`     | Query      | *(required)*             | The Kafka topic to consume.                                                                                            |
| `file_path` | Query      | *(required)*             | Local path where consumed messages will be appended.                                                                   |
| `group_id`  | Query      | `demo-consumer-group`    | Kafka consumer group ID. Consumers in the same group share partition assignments.                                      |
| `client_id` | Query      | None                     | Optional friendly name for the consumer. Shown as the Kafka `client_id` and used as the thread name for easier tracking.|

### Behavior Notes
- If `group_id` is shared by multiple consumers reading a single-partition topic, only one consumer actually receives messages due to how Kafka rebalances partitions. For load balancing across multiple consumers, **increase your topic partition count**.
- If `client_id` is omitted, a default name is assigned to both the thread and Kafka’s `client_id`.

---

## Scaling & Partitioning Notes

- **Thread-based** concurrency works well for **I/O-bound** tasks like Kafka consumption. If you have heavy CPU-bound processing, consider using **multiprocessing** or an external task queue (e.g., Celery).  
- **Kafka partitioning**: To distribute messages across multiple consumers in the same group, you need multiple partitions on your topic. A single-partition topic can only be consumed by one consumer at a time within the same group.  
- **Monitoring**: Tools like `kafka-consumer-groups.sh` or external dashboards (e.g., Conduktor, Burrow) can help you track consumer lag and partition assignments.

---
