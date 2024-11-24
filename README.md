# Kafka Consumer Offset Monitor POC

![Kafka Logo](https://kafka.apache.org/images/project_logo.svg)

## Table of Contents

- [Kafka Consumer Offset Monitor POC](#kafka-consumer-offset-monitor-poc)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Motivation and Purpose](#motivation-and-purpose)
  - [Features](#features)
  - [Architecture](#architecture)
  - [Module Introduction](#module-introduction)
    - [Kafka Module](#kafka-module)
    - [Python Modules](#python-modules)
      - [Producer](#producer)
      - [Consumer](#consumer)
      - [Consumer Offset Monitor](#consumer-offset-monitor)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Configuration](#configuration)
  - [Running the POC](#running-the-poc)
    - [1. Start the Kafka Cluster](#1-start-the-kafka-cluster)
    - [2. Run the Producer](#2-run-the-producer)
    - [3. Run the Consumer](#3-run-the-consumer)
    - [4. Run the Consumer Offset Monitor](#4-run-the-consumer-offset-monitor)
  - [Usage Examples](#usage-examples)
    - [Producing Messages](#producing-messages)
    - [Consuming Messages](#consuming-messages)
    - [Monitoring Consumer Offsets](#monitoring-consumer-offsets)
  - [Troubleshooting](#troubleshooting)
    - [Common Issues](#common-issues)
    - [Steps to Resolve Issues](#steps-to-resolve-issues)
  - [Contributing](#contributing)
  - [License](#license)
  - [Acknowledgments](#acknowledgments)

---

## Overview

This Proof of Concept (POC) demonstrates how to interact with an Apache Kafka cluster using Python. It includes:

- **Producer Script**: Sends messages to a Kafka topic.
- **Consumer Script**: Consumes messages from a Kafka topic within a specified consumer group.
- **Consumer Offset Monitor Script**: Monitors and displays the offsets and lag of consumers within a consumer group, replicating the functionality of Kafka's `kafka-consumer-groups.sh` tool.

## Motivation and Purpose

Monitoring consumer group offsets is crucial for ensuring that Kafka consumers are processing messages efficiently and without falling behind. Understanding the lag (the difference between the latest message in a partition and the last message consumed) helps in identifying performance bottlenecks and ensuring data is processed in a timely manner.

This POC aims to:

- Provide a comprehensive understanding of Kafka's consumer group mechanics.
- Demonstrate how to programmatically monitor consumer offsets using Python.
- Replicate the functionality of Kafka's native monitoring tools using the `kafka-python` library.

## Features

- **Message Production**: Send structured JSON messages to a Kafka topic.
- **Message Consumption**: Consume messages from a Kafka topic using a designated consumer group.
- **Offset Monitoring**: Display detailed information about consumer group offsets, including current offsets, log end offsets, and lag for each partition.
- **Error Handling**: Robust error handling to manage common issues such as missing topics or inactive consumer groups.
- **Modular Design**: Separate scripts for producing, consuming, and monitoring to maintain clarity and modularity.

## Architecture

The POC consists of three primary Python scripts interacting with an Apache Kafka cluster:

1. **Producer (`producer.py`)**: Publishes messages to a Kafka topic.
2. **Consumer (`consumer.py`)**: Subscribes to a Kafka topic as part of a consumer group and processes incoming messages.
3. **Consumer Offset Monitor (`consumer_offset_monitor.py`)**: Monitors and displays the status of consumer group offsets, including lag metrics.

All scripts communicate with the Kafka cluster via the `kafka-python` library, leveraging Kafka's APIs for administrative and consumer operations.

![Architecture Diagram](https://i.imgur.com/Z4gHtVX.png) <!-- Placeholder for an actual architecture diagram -->

## Module Introduction

### Kafka Module

- **Apache Kafka**: A distributed streaming platform capable of handling real-time data feeds. It allows for publishing and subscribing to streams of records, storing them in a fault-tolerant manner, and processing them as they occur.

### Python Modules

#### Producer

- **Script**: `producer.py`
- **Purpose**: Sends structured JSON messages to a specified Kafka topic.
- **Key Features**:
  - Configurable message content.
  - Automatic topic creation if it doesn't exist.
  - Logs each produced message for verification.

#### Consumer

- **Script**: `consumer.py`
- **Purpose**: Consumes messages from a specified Kafka topic as part of a designated consumer group.
- **Key Features**:
  - Subscribes to a topic within a consumer group.
  - Automatically commits offsets to track consumption progress.
  - Processes and displays consumed messages in real-time.

#### Consumer Offset Monitor

- **Script**: `consumer_offset_monitor.py`
- **Purpose**: Monitors and displays the status of consumer group offsets, including current offsets, log end offsets, and lag for each partition.
- **Key Features**:
  - Lists all available Kafka topics.
  - Creates a topic if it doesn't exist.
  - Describes consumer group details, including state, protocol, and members.
  - Fetches and displays current offsets, log end offsets, and calculates lag.
  - Retrieves and displays the latest `n` events from the topic for verification.

## Getting Started

### Prerequisites

- **Python 3.6+**
- **Apache Kafka Cluster**: Running locally or accessible remotely.
- **Docker** (optional): For setting up Kafka using Docker Compose.
- **`kafka-python` Library**: Python client for Kafka.

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/your-username/kafka-consumer-offset-monitor-poc.git
   cd kafka-consumer-offset-monitor-poc
   ```

2. **Set Up a Virtual Environment**

   It's recommended to use a Python virtual environment to manage dependencies.

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Unix or MacOS
   venv\Scripts\activate     # On Windows
   ```

3. **Upgrade `pip`**

   ```bash
   pip install --upgrade pip
   ```

4. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   **Note**: If `requirements.txt` does not exist, install `kafka-python` directly:

   ```bash
   pip install kafka-python
   ```

### Configuration

1. **Kafka Cluster**

   Ensure that your Kafka cluster is running. For local development, you can use Docker Compose.

2. **Environment Variables (Optional)**

   You can configure your scripts using environment variables for flexibility and security.

   - **Create a `.env` File**

     ```env
     BOOTSTRAP_SERVERS=localhost:9092
     TOPIC=sample-topic
     GROUP_ID=sample-consumer-group
     NUM_EVENTS=5
     ```

   - **Load Environment Variables in Scripts**

     Modify your scripts to load these variables using `python-dotenv`.

     ```python
     from dotenv import load_dotenv
     import os

     load_dotenv()

     bootstrap_servers = os.getenv('BOOTSTRAP_SERVERS').split(',')
     topic = os.getenv('TOPIC')
     group_id = os.getenv('GROUP_ID')
     n = int(os.getenv('NUM_EVENTS', 5))
     ```

## Running the POC

### 1. Start the Kafka Cluster

For local development, use Docker Compose to set up Kafka and Zookeeper.

1. **Create a `docker-compose.yml` File**

   ```yaml
   version: '2'
   services:
     zookeeper:
       image: confluentinc/cp-zookeeper:latest
       environment:
         ZOOKEEPER_CLIENT_PORT: 2181
         ZOOKEEPER_TICK_TIME: 2000

     kafka:
       image: confluentinc/cp-kafka:latest
       depends_on:
         - zookeeper
       ports:
         - "9092:9092"
       environment:
         KAFKA_BROKER_ID: 1
         KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
         KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
         KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
   ```

2. **Start the Services**

   ```bash
   docker-compose up -d
   ```

3. **Verify Kafka is Running**

   ```bash
   docker-compose ps
   ```

   **Expected Output:**

   ```
   Name                 Command               State                Ports
   --------------------------------------------------------------------------------
   kafka-poc_kafka_1    /etc/confluent/docker/run    Up      0.0.0.0:9092->9092/tcp
   kafka-poc_zookeeper_1 /etc/confluent/docker/run  Up      2181/tcp
   ```

### 2. Run the Producer

The producer script sends JSON-formatted messages to the Kafka topic.

1. **Ensure the Kafka Cluster is Running**

   Verify that Kafka is up by checking the Docker containers or using Kafka's CLI tools.

2. **Execute the Producer Script**

   ```bash
   python producer.py
   ```

   **Expected Output:**

   ```
   Produced message to topic 'sample-topic': {'id': 1, 'timestamp': 1732469401025, 'value': 26, 'message': 'Sample message 1'}
   Produced message to topic 'sample-topic': {'id': 2, 'timestamp': 1732469401535, 'value': 78, 'message': 'Sample message 2'}
   ...
   ```

   **Note**: The producer automatically creates the `sample-topic` if it doesn't exist.

### 3. Run the Consumer

The consumer subscribes to the Kafka topic and consumes messages as part of the specified consumer group.

1. **Execute the Consumer Script**

   Open a new terminal window/tab, activate your virtual environment, and run:

   ```bash
   python consumer.py
   ```

   **Expected Output:**

   ```
   Consuming messages from topic 'sample-topic' in group 'sample-consumer-group'...
   Consumed message: {'id': 1, 'timestamp': 1732469401025, 'value': 26, 'message': 'Sample message 1'}
   Consumed message: {'id': 2, 'timestamp': 1732469401535, 'value': 78, 'message': 'Sample message 2'}
   ...
   ```

   **Note**: Keep this consumer running to ensure the consumer group remains active.

### 4. Run the Consumer Offset Monitor

This script monitors the consumer group's offsets and displays lag metrics.

1. **Execute the Consumer Offset Monitor Script**

   In a separate terminal window/tab, activate your virtual environment, and run:

   ```bash
   python consumer_offset_monitor.py --bootstrap-servers localhost:9092 --topic sample-topic --group-id sample-consumer-group --num-events 5
   ```

   **Expected Output:**

   ```
   Topic 'sample-topic' already exists.
   Available topics: ['__consumer_offsets', 'sample-topic']

   Type of group_description: <class 'kafka.structs.GroupInformation'>
   Attributes of group_description: ['__add__', '__class__', '__class_getitem__', '__contains__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getitem__', '__getnewargs__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__iter__', '__le__', '__len__', '__lt__', '__match_args__', '__module__', '__mul__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__rmul__', '__setattr__', '__sizeof__', '__slots__', '__str__', '__subclasshook__', '_asdict', '_field_defaults', '_fields', '_make', '_replace', 'authorized_operations', 'count', 'error_code', 'group', 'index', 'members', 'protocol', 'protocol_type', 'state']

   Group: sample-consumer-group
   State: Stable
   Protocol: consumer
   Protocol Type: consumer
   Members:
   CONSUMER-ID                                     HOST                 CLIENT-ID          
   ------------------------------------------------------------------------------------------
   sample-consumer-group-1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx  /127.0.0.1          consumer1          

   Offsets:
   TOPIC                PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG       
   ----------------------------------------------------------------------
   sample-topic         0          10              10              0         
   sample-topic         1          0               0               N/A        

   Latest 5 events from topic 'sample-topic':
   {'topic': 'sample-topic', 'partition': 0, 'offset': 6, 'key': 'key-7', 'value': {'id': 7, 'timestamp': 1732469404060, 'value': 66, 'message': 'Sample message 7'}, 'timestamp': 1732469404060}
   {'topic': 'sample-topic', 'partition': 0, 'offset': 7, 'key': 'key-8', 'value': {'id': 8, 'timestamp': 1732469404564, 'value': 96, 'message': 'Sample message 8'}, 'timestamp': 1732469404564}
   {'topic': 'sample-topic', 'partition': 0, 'offset': 8, 'key': 'key-9', 'value': {'id': 9, 'timestamp': 1732469405070, 'value': 55, 'message': 'Sample message 9'}, 'timestamp': 1732469405070}
   {'topic': 'sample-topic', 'partition': 0, 'offset': 9, 'key': 'key-10', 'value': {'id': 10, 'timestamp': 1732469405576, 'value': 36, 'message': 'Sample message 10'}, 'timestamp': 1732469405576}
   ```

   **Explanation:**

   - **Group Details**: Displays information about the consumer group, including its state and members.
   - **Offsets**: Shows current offsets, log end offsets, and lag for each partition.
   - **Latest Events**: Displays the latest `n` events from the topic for verification.

## Usage Examples

### Producing Messages

Run the producer script to send messages to the Kafka topic.

```bash
python producer.py
```

**Sample Output:**

```
Produced message to topic 'sample-topic': {'id': 1, 'timestamp': 1732469401025, 'value': 26, 'message': 'Sample message 1'}
Produced message to topic 'sample-topic': {'id': 2, 'timestamp': 1732469401535, 'value': 78, 'message': 'Sample message 2'}
...
```

### Consuming Messages

Run the consumer script to consume messages from the Kafka topic.

```bash
python consumer.py
```

**Sample Output:**

```
Consuming messages from topic 'sample-topic' in group 'sample-consumer-group'...
Consumed message: {'id': 1, 'timestamp': 1732469401025, 'value': 26, 'message': 'Sample message 1'}
Consumed message: {'id': 2, 'timestamp': 1732469401535, 'value': 78, 'message': 'Sample message 2'}
...
```

### Monitoring Consumer Offsets

Run the consumer offset monitor to view consumer group offsets and lag.

```bash
python consumer_offset_monitor.py --bootstrap-servers localhost:9092 --topic sample-topic --group-id sample-consumer-group --num-events 5
```

**Sample Output:**

```
Topic 'sample-topic' already exists.
Available topics: ['__consumer_offsets', 'sample-topic']

Type of group_description: <class 'kafka.structs.GroupInformation'>
Attributes of group_description: ['__add__', '__class__', '__class_getitem__', '__contains__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getitem__', '__getnewargs__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__iter__', '__le__', '__len__', '__lt__', '__match_args__', '__module__', '__mul__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__rmul__', '__setattr__', '__sizeof__', '__slots__', '__str__', '__subclasshook__', '_asdict', '_field_defaults', '_fields', '_make', '_replace', 'authorized_operations', 'count', 'error_code', 'group', 'index', 'members', 'protocol', 'protocol_type', 'state']

Group: sample-consumer-group
State: Stable
Protocol: consumer
Protocol Type: consumer
Members:
CONSUMER-ID                                     HOST                 CLIENT-ID          
------------------------------------------------------------------------------------------
sample-consumer-group-1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx  /127.0.0.1          consumer1          

Offsets:
TOPIC                PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG       
----------------------------------------------------------------------
sample-topic         0          10              10              0         
sample-topic         1          0               0               N/A        

Latest 5 events from topic 'sample-topic':
{'topic': 'sample-topic', 'partition': 0, 'offset': 6, 'key': 'key-7', 'value': {'id': 7, 'timestamp': 1732469404060, 'value': 66, 'message': 'Sample message 7'}, 'timestamp': 1732469404060}
{'topic': 'sample-topic', 'partition': 0, 'offset': 7, 'key': 'key-8', 'value': {'id': 8, 'timestamp': 1732469404564, 'value': 96, 'message': 'Sample message 8'}, 'timestamp': 1732469404564}
{'topic': 'sample-topic', 'partition': 0, 'offset': 8, 'key': 'key-9', 'value': {'id': 9, 'timestamp': 1732469405070, 'value': 55, 'message': 'Sample message 9'}, 'timestamp': 1732469405070}
{'topic': 'sample-topic', 'partition': 0, 'offset': 9, 'key': 'key-10', 'value': {'id': 10, 'timestamp': 1732469405576, 'value': 36, 'message': 'Sample message 10'}, 'timestamp': 1732469405576}
```

## Troubleshooting

### Common Issues

1. **AttributeError: 'GroupInformation' object has no attribute 'group_id'**

   **Cause**: Attempting to access a non-existent `group_id` attribute. The correct attribute is `group`.

   **Solution**: Update the script to use `group_description.group` instead of `group_description.group_id`.

2. **Consumer Group Does Not Exist**

   **Cause**: No active consumer is connected to the specified consumer group.

   **Solution**: Ensure that the consumer script is running and connected to the consumer group before attempting to monitor it.

3. **Kafka Not Running**

   **Cause**: Kafka broker is not running or not accessible.

   **Solution**: Verify that Kafka is running using Docker Compose or your preferred method. Check network configurations and ports.

4. **Topic Does Not Exist**

   **Cause**: Specified Kafka topic does not exist.

   **Solution**: The producer script automatically creates the topic if it doesn't exist. Ensure that the producer is running to create the topic, or manually create it using Kafka's CLI tools.

### Steps to Resolve Issues

1. **Verify Kafka Cluster Status**

   ```bash
   docker-compose ps
   ```

   Ensure that both Zookeeper and Kafka services are up and running.

2. **Check Installed `kafka-python` Version**

   ```bash
   pip show kafka-python
   ```

   Ensure you have version `2.0.0` or higher.

3. **Reinstall `kafka-python`**

   ```bash
   pip uninstall kafka-python
   pip install kafka-python
   ```

4. **Ensure Active Consumer Group**

   Run the consumer script to ensure the consumer group is active.

   ```bash
   python consumer.py
   ```

5. **Use Minimal Monitor for Debugging**

   Use `minimal_monitor.py` to inspect the structure of the `GroupInformation` object.

   ```python
   # minimal_monitor.py
   
   from kafka import KafkaAdminClient
   import sys
   
   def minimal_monitor(bootstrap_servers, group_id):
       try:
           admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers, client_id='minimal-monitor')
           consumer_groups = admin_client.describe_consumer_groups([group_id])
           admin_client.close()
   
           if not consumer_groups:
               print(f"Consumer group '{group_id}' does not exist.")
               sys.exit(1)
   
           group_description = consumer_groups[0]
   
           # Print type and attributes
           print(f"Type of group_description: {type(group_description)}")
           print(f"Attributes of group_description: {dir(group_description)}\n")
   
           # Print group details
           print(f"Group ID: {group_description.group}")
           print(f"State: {group_description.state}")
           print(f"Protocol: {group_description.protocol}")
           print(f"Protocol Type: {group_description.protocol_type}")
           print(f"Number of Members: {len(group_description.members)}")
   
       except AttributeError as ae:
           print(f"Attribute error: {ae}")
           print("Please ensure you are using the latest version of kafka-python.")
           sys.exit(1)
       except Exception as e:
           print(f"Error: {e}")
           sys.exit(1)
   
   def main():
       import argparse
       parser = argparse.ArgumentParser(description='Minimal Kafka Consumer Group Monitor')
       parser.add_argument('--bootstrap-servers', required=True, nargs='+', help='Kafka bootstrap servers (e.g., localhost:9092)')
       parser.add_argument('--group-id', required=True, help='Consumer group ID')
   
       args = parser.parse_args()
   
       bootstrap_servers = args.bootstrap_servers
       group_id = args.group_id
   
       minimal_monitor(bootstrap_servers, group_id)
   
   if __name__ == "__main__":
       main()
   ```

   **Run the Minimal Script**

   ```bash
   python minimal_monitor.py --bootstrap-servers localhost:9092 --group-id sample-consumer-group
   ```

   **Expected Output:**

   ```
   Type of group_description: <class 'kafka.structs.GroupInformation'>
   Attributes of group_description: ['__add__', '__class__', '__class_getitem__', '__contains__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getitem__', '__getnewargs__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__iter__', '__le__', '__len__', '__lt__', '__match_args__', '__module__', '__mul__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__rmul__', '__setattr__', '__sizeof__', '__slots__', '__str__', '__subclasshook__', '_asdict', '_field_defaults', '_fields', '_make', '_replace', 'authorized_operations', 'count', 'error_code', 'group', 'index', 'members', 'protocol', 'protocol_type', 'state']

   Group ID: sample-consumer-group
   State: Stable
   Protocol: consumer
   Protocol Type: consumer
   Number of Members: 1
   ```

   **Interpretation**: Confirms that `group_description.group` is the correct attribute to access the consumer group ID.

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. **Fork the Repository**

2. **Create a Feature Branch**

   ```bash
   git checkout -b feature/YourFeatureName
   ```

3. **Commit Your Changes**

   ```bash
   git commit -m "Add Your Feature"
   ```

4. **Push to the Branch**

   ```bash
   git push origin feature/YourFeatureName
   ```

5. **Open a Pull Request**

   Submit a pull request describing your changes.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- [Apache Kafka](https://kafka.apache.org/) - The distributed streaming platform.
- [kafka-python](https://github.com/dpkp/kafka-python) - Python client for Kafka.
- [Confluent](https://www.confluent.io/) - Providers of Kafka-related services and tools.
- [Docker](https://www.docker.com/) - Containerization platform used for setting up Kafka locally.

---

**Happy Streaming! 🚀**