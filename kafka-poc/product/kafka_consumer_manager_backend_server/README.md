# Kafka Consumer Manager Backend

This project provides a **thread-based** Kafka consumer management system, built with **Python** and **FastAPI**. Each Kafka consumer runs in its own thread, allowing you to **create**, **start**, **pause**, **resume**, and **terminate** consumers via a simple REST API.

---

## 1. Project Overview

### Folder Structure

```plaintext
kafka_consumer_manager_backend_server/
├── consumers/
│   ├── __init__.py
│   ├── consumer_thread.py
│   └── manager.py
├── outputA.txt
└── server.py
```

1. **`consumers/consumer_thread.py`**  
   - Defines the `ConsumerThread` class, a subclass of `threading.Thread` that manages a single Kafka consumer loop.  
   - Supports pausing (via a `pause_event`) and stopping (via a `stop_event`).  

2. **`consumers/manager.py`**  
   - Contains `ThreadManager`, which tracks all consumers (threads) in a dictionary.  
   - Provides methods to create, start, pause, and terminate consumers, and to monitor active threads.

3. **`server.py`**  
   - A **FastAPI** application exposing REST endpoints to manage the lifecycle of each consumer.  
   - On application shutdown, it terminates all running consumers to ensure a clean exit.

4. **`outputA.txt`**  
   - An example output file for messages consumed by a thread (can be replaced or removed).

---

## 2. How the System Works

1. **Creating a Consumer**  
   - You call `POST /create-consumer` with JSON containing broker info, topic, file path, etc.  
   - The system creates a record and (optionally) starts the consumer thread.  

2. **Starting and Pausing**  
   - **Start** or **Resume**: Moves a consumer from `CREATED` or `PAUSED` to `RUNNING`.  
   - **Pause**: Temporarily halts message consumption but keeps the thread alive.

3. **Terminating**  
   - Fully stops the consumer thread, sets status to `TERMINATED`, and removes it from the manager’s dictionary.  
   - Ensures resources (like file handles, Kafka sockets) are closed.

4. **Thread Monitoring**  
   - The `monitor_threads()` method enumerates all Python threads (via `threading.enumerate()`) and marks which are recognized as consumer threads.  
   - A `GET /monitor-threads` endpoint can show a snapshot of all active threads, verifying no leftover or “zombie” threads remain.

---

## 3. Key Python Threading Concepts

1. **Thread Subclass**  
   - `ConsumerThread` extends `threading.Thread` and overrides `run()`.  
   - Inside `run()`, a `KafkaConsumer` is created, and messages are read in a loop until a stop event is set or an error occurs.

2. **Events for Control**  
   - **`stop_event`**: Signals the thread to break out of the consumption loop and exit gracefully.  
   - **`pause_event`**: If set, the thread sleeps or skips reading messages, effectively “pausing” consumption without shutting down the consumer.

3. **Resource Cleanup**  
   - In a `finally:` block, each consumer closes the KafkaConsumer and flushes/close any file handles.  
   - The manager calls `thread.join()` to ensure the thread is fully finished before removing references.

4. **Error Propagation**  
   - On startup, if the consumer can’t connect (e.g., `NoBrokersAvailable`), the thread sets an error flag. The manager checks this and raises the exception so the FastAPI endpoint can return an HTTP error to the client.

---

## 4. Performance Considerations

1. **I/O-Bound Threads**  
   - Because these threads spend much of their time waiting on network I/O from Kafka, Python’s GIL typically isn’t a major bottleneck.  
   - Each consumer can operate concurrently, reading messages from Kafka in parallel.

2. **Number of Threads**  
   - Each thread has a stack (a few MB by default). Creating hundreds or thousands of consumers can lead to significant memory usage.  
   - If you need massive scale, consider using a pool or an async approach.

3. **Pausing vs. Terminating**  
   - Pausing a thread is cheaper than terminating and re-creating it if you plan to resume soon.  
   - However, a paused thread still consumes some resources (e.g., memory for the stack). If you have many paused consumers, consider terminating them if they won’t resume soon.

---

## 5. Preventing Out-of-Memory (OOM) Issues

1. **Limit the Thread Count**  
   - Each consumer spawns a dedicated thread. In production, watch for excessive consumer creation or “idle” paused consumers.  
   - If the environment demands many partitions or topics, ensure you have enough system memory or switch to a more scalable approach.

2. **Avoid Large In-Memory Buffers**  
   - The consumer writes messages directly to a file (`outputA.txt` by default).  
   - If you need to process large messages in memory, do so in a streaming/chunked fashion to avoid building huge data structures.

3. **Proper Shutdown**  
   - On error or normal shutdown, each thread calls `KafkaConsumer.close()`. The manager calls `thread.join()`, ensuring memory for that thread is freed.  
   - A `finally:` block in `consumer_thread.py` ensures resources are released even if an exception occurs.

4. **Monitor Memory Usage**  
   - Tools like `psutil` or external monitoring (Docker, Kubernetes) can track memory usage.  
   - If usage grows unexpectedly, check for leftover references or un-terminated threads.

---

## 6. Usage and API Endpoints

1. **Run the Server**  
   ```bash
   cd kafka_consumer_manager_backend_server
   python server.py
   # or
   uvicorn server:app --host 0.0.0.0 --port 8000
   ```

2. **Endpoints**  
   - `POST /create-consumer`  
     - Body: `{"name": "ConsumerA", "broker": "localhost:9092", "topic": "TopicA", "file_path": "./outputA.txt", "auto_start": true}`  
     - Creates a new consumer record (and optionally starts the thread).  
   - `POST /start-consumer`  
     - Body: `{"consumer_id": "<id>"}`  
     - Resumes or starts a consumer if it’s `CREATED` or `PAUSED`.  
   - `POST /pause-consumer`  
     - Body: `{"consumer_id": "<id>"}`  
     - Pauses a `RUNNING` consumer.  
   - `POST /terminate-consumer`  
     - Body: `{"consumer_id": "<id>"}`  
     - Fully stops and removes the consumer.  
   - `GET /list-consumers`  
     - Returns an array of metadata for all known consumers (ID, broker, status, etc.).  
   - `GET /monitor-threads`  
     - Shows all active Python threads and whether each is recognized as a consumer thread.

---

## 7. Future Enhancements

1. **Advanced Error Handling**  
   - If a consumer encounters an error mid-run (e.g., broker downtime), you might set a status like `ERROR` and expose it in `list-consumers`.

2. **Thread Pools or Async**  
   - If you need to manage hundreds or thousands of partitions, a one-thread-per-partition approach may not scale well. Consider an async approach or a distributed queue system (e.g., Celery, Kafka Streams, etc.).

3. **Metrics and Monitoring**  
   - Tools like `prometheus_client` or `psutil` can gather CPU/memory usage and expose them to a metrics endpoint.

---
