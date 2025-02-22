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

The following summary is a complete lifecycle explanation—from the overall architecture to each thread (including the main thread and worker threads)—designed to let you understand the entire workflow from start to finish.

---

## 1. Overall Operational Architecture

- **Application Starting Point**  
  In the `if __name__ == "__main__":` block of `server.py`, the following call is made:
  ```python
  uvicorn.run(app, host="0.0.0.0", port=8000)
  ```  
  This line of code starts the uvicorn server, which in turn launches the FastAPI application. At this point, the main thread enters the asyncio event loop created by uvicorn and remains blocked waiting for external HTTP requests.

- **API Request Dispatching**  
  When an external request is sent (for example, `/start-consumer`, `/stop-consumer`, etc.), the uvicorn event loop routes the request to the corresponding FastAPI endpoint. The execution of these endpoints (either by a worker thread or as an async coroutine) will call methods in our custom `ThreadManager` to manipulate threads.

---

## 2. Main Thread and the uvicorn Event Loop

- **Main Thread Entering Wait State**  
  The `run()` method of uvicorn creates and starts an asyncio event loop. Internally, the server calls in `server.run()` (in single-worker mode):
  ```python
  asyncio.run(self.serve(sockets=sockets))
  ```
  
  ![Screenshot 2025-02-22 at 5.07.20 PM](https://hackmd.io/_uploads/r1dRmMPcke.png)

  In this process, the `serve()` function further calls `await self._serve(sockets)`. During this process, the server completes its startup, binds the socket, and calls `await self.startup(sockets)`.  
  Then, the server enters the coroutine `await self.main_loop()`, where the loop waits using `await asyncio.sleep(0.1)` to periodically check if it needs to exit.  
  In other words, **the main thread primarily waits for new events and requests within the asyncio event loop established by uvicorn (especially at the sleep call in the `main_loop()` coroutine)**.

- **Dispatching API Requests**  
  When a new HTTP request arrives, the uvicorn event loop immediately dispatches the request to FastAPI for handling, while the main thread (or other workers within the event loop) returns to a waiting state.

---

## 3. Operation Process of ThreadManager and ConsumerThread

### 3.1 When Receiving a `/start-consumer` Request

1. **API Endpoint is Called**  
   The FastAPI route `/start-consumer` is triggered, and at this time, the thread processing the request (usually from a uvicorn worker or coroutine) executes the `start_consumer()` function.

2. **Calling ThreadManager.start_consumer**  
   Within this function, a new ConsumerThread object is created based on the passed parameters.  
   - **Object Instantiation:**  
     In `ConsumerThread.__init__`, the Kafka broker, topic, file path, group_id, client_id are set, and a `stop_event` is created (used for subsequent stop notifications).
     
  ![Screenshot 2025-02-22 at 5.08.42 PM](https://hackmd.io/_uploads/SkkNNfv9Jl.png)
  
  ![Screenshot 2025-02-22 at 5.09.22 PM](https://hackmd.io/_uploads/BkZ8VGw5Jl.png)

3. **Starting a New Thread**  
   Immediately thereafter, `ConsumerThread.start()` is called.  
   - This call **does not block** the API thread that invoked it; it merely forks a new worker thread within the same process and automatically calls the object's `run()` method.

4. **Responding to the API Request**  
   The ThreadManager returns the unique consumer_id generated, and the API endpoint returns a JSON response. The main thread or the API handling thread then immediately returns to a waiting state.

---

### 3.2 Lifecycle of ConsumerThread

1. **Instantiation:**  
   - In `__init__`, basic parameters are set, a `stop_event` is created, and the thread name is configured (if a client_id is provided, it is used as the name).

2. **Start:**  
   - After calling `start()`, the system creates a new OS thread under the same PID, and this new thread automatically executes the `run()` method.

3. **Running:**  
   - **Initialize KafkaConsumer:** In the `run()` method, a KafkaConsumer is created and subscribes to the specified topic.  
   - **Enter Consumption Loop:** The specified file is opened in append mode for writing, and an infinite loop is entered. In each iteration of the loop:  
     - It checks `self.stop_event.is_set()`: if it has not been set, it continues.  
     - It consumes a message from Kafka, decodes it, writes it to the file, and then simulates a processing delay with `time.sleep(0.1)`.  
   - **Exception and Exit:** If a stop signal is received (or an error occurs) in the loop, it breaks out of the loop, closes the KafkaConsumer, and exits the `run()` method.

4. **Stop:**  
   - When a `/stop-consumer` request is received, the ThreadManager calls `ConsumerThread.stop()`.  
   - This method sets the `stop_event`, causing the running loop to detect it, exit, and complete cleanup.

5. **Termination:**  
   - Next, the ThreadManager calls `join()` to wait for the thread to completely exit.  
   - When the `run()` method ends, the thread officially terminates, the OS releases its resources, and the thread record is removed from the manager’s dictionary.

---

### 3.3 When Receiving a `/stop-consumer` Request

1. **API Endpoint is Called**  
   The FastAPI route `/stop-consumer/{consumer_id}` is triggered, and the corresponding API handling thread executes `stop_consumer(consumer_id)`.

2. **Calling ThreadManager.stop_consumer**  
   The manager finds the corresponding ConsumerThread based on the consumer_id.  
   - It calls `thread.stop()` (to set the stop event).  
   - It calls `thread.join(timeout=10)`, an operation that will block the API handling thread while waiting for the worker thread to gracefully exit.

3. **Response and Cleanup**  
   If the thread exits gracefully, it is removed from the management structure and a success response is returned; if it does not exit within the specified time, a warning is issued, but ultimately the API response will return the stop result.

---

## 4. Summary of the Overall Workflow and Lifecycle

1. **Main Thread (uvicorn Event Loop):**  
   - After `uvicorn.run(app, ...)` is initiated, the main thread creates an asyncio event loop and enters `server.run()`, then enters the `await self.main_loop()` coroutine to continuously wait (for example, at the `await asyncio.sleep(0.1)` call).  
   - It is responsible for listening for external HTTP requests and dispatching them to the corresponding API handling threads or coroutines.

2. **API Request Handling (FastAPI Endpoint):**  
   - When a request comes in (for example, to start or stop a consumer), the corresponding API handling function is triggered and calls the ThreadManager from within a worker thread.  
   - These calls include creating a ConsumerThread (and starting a new thread via `start()`) or stopping a ConsumerThread (using `stop()` and waiting for exit with `join()`).

3. **Lifecycle of ConsumerThread (Worker Thread):**  
   - **Instantiation:** Setting parameters via `__init__` and creating the stop event.  
   - **Start:** Calling `start()` forks a new thread within the same process and begins executing the `run()` method.  
   - **Running:**  
     - Creating a KafkaConsumer and connecting.  
     - Entering an endless loop to continuously consume messages while checking for the stop event.  
     - Writing messages to a file and waiting (sleep).  
   - **Stop:** Upon receiving an external stop command, the `stop()` method is called to set the stop event, causing the loop to exit.  
   - **Termination:** Calling `join()` to wait for the thread to exit, after which it is removed from the management structure and the OS reclaims the thread’s resources.

---

This entire process ensures that:  
- The main thread always waits for new requests in uvicorn's asyncio event loop and is not blocked by the newly started ConsumerThread (unless the API handling logic includes synchronous calls such as join).  
- When an API request arrives, FastAPI dynamically manages worker threads through the ThreadManager, handling start, stop, and status queries accordingly.  
- Each ConsumerThread—from instantiation and starting, to continuous running, and finally to receiving a stop signal and gracefully exiting—constitutes a complete thread lifecycle.

This is the complete explanation of every stage, from the main thread to the worker threads, and through the entire application workflow.

Below is a simple ASCII flowchart that simulates the complete process from the main process (PID) starting uvicorn (i.e., the main thread), to forking out a ConsumerThread upon receiving the start-consumer command, and then stopping the thread upon receiving the stop-consumer command:

```
┌─────────────────────────────────────────┐
│                Process (PID)            │
│                                         │
│  ┌─────────────────────────────────────┐  │
│  │           Main Thread               │  │
│  │ (uvicorn/ubicomp Event Loop)        │  │
│  │   ┌─────────────────────────────┐   │  │
│  │   │Waiting and Dispatching HTTP │◄──┼─────┐
│  │   │ Requests (API)              │   │     │
│  │   └─────────────────────────────┘   │     │
│  └─────────────────────────────────────┘     │
└─────────────────────────────────────────┘     │
                                              │   │
                                              │   │
                             ┌────────────────┴───┴─────────────┐
                             │        API Command Received      │
                             │       (e.g., start-consumer)       │
                             └────────────────┬────────────────────┘
                                              │
                                              ▼
                    ┌────────────────────────────────────────┐
                    │      ThreadManager.start_consumer      │
                    │  ──> Generate consumer_id              │
                    │  ──> Create ConsumerThread object       │
                    │  ──> Call thread.start()                │
                    └────────────────────────────────────────┘
                                              │
                                              ▼
                    ┌────────────────────────────────────────┐
                    │           ConsumerThread               │
                    │   ┌────────────────────────────────┐   │
                    │   │        Life Cycle:             │   │
                    │   │ __init__ (set parameters and   │   │
                    │   │       stop_event)              │   │
                    │   │      ↓                       │   │
                    │   │  start() → New thread created  │   │
                    │   │      ↓                       │   │
                    │   │  run() execution starts:       │   │
                    │   │      ┌────────────────────┐    │   │
                    │   │      │ Create KafkaConsumer│    │   │
                    │   │      │ Enter consumption   │    │   │
                    │   │      │ loop (continuously    │    │   │
                    │   │      │ consuming messages)   │    │   │
                    │   │      └────────────────────┘    │   │
                    │   └────────────────────────────────┘   │
                    └────────────────────────────────────────┘
                                              │
                                              │
                                              │
                        ┌─────────────────────┴────────────────────────┐
                        │      API Command Received: stop-consumer     │
                        │     (corresponding to ThreadManager.stop_consumer)│
                        └─────────────────────┬────────────────────────┘
                                              │
                                              ▼
                    ┌────────────────────────────────────────┐
                    │      ConsumerThread.stop() is called   │
                    │   (set stop_event, notify loop to exit)  │
                    └────────────────────────────────────────┘
                                              │
                                              ▼
                    ┌────────────────────────────────────────┐
                    │ Call thread.join() in the API handling │
                    │ thread to wait for ConsumerThread’s    │
                    │        graceful exit                   │
                    └────────────────────────────────────────┘
                                              │
                                              ▼
                    ┌────────────────────────────────────────┐
                    │ ConsumerThread completes run() and     │
                    │   terminates (OS releases thread       │
                    │   resources, manager removes record)   │
                    └────────────────────────────────────────┘
```

---

### Explanation

1. **Main Thread**  
   • Starting from time 0, the main thread is continuously waiting for and processing HTTP requests in the uvicorn event loop.  
   • At 5 seconds, upon receiving the start-consumer API request, the main thread calls `start_consumer` via the ThreadManager, forking a new ConsumerThread (this process does not block the main thread).

2. **ConsumerThread**  
   • Once forked, it immediately enters its own `run()` method, creates a KafkaConsumer, and enters a continuous loop for consuming messages.  
   • During this period, the ConsumerThread operates concurrently with the main thread.

3. **Stopping ConsumerThread**  
   • At 15 seconds, upon receiving the stop-consumer API request, the main thread (or the API handling thread) calls the ThreadManager’s `stop_consumer`, which in turn calls ConsumerThread’s `stop()` (setting the stop event).  
   • Then, `join()` is called to wait for the ConsumerThread to gracefully exit.  
   • Once ConsumerThread detects that the stop_event is set, it exits the loop, completes cleanup, and terminates. At this point, `join()` returns, and the ConsumerThread has completely exited with its resources released.


