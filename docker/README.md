# Kafka Cluster with Docker Compose

This repository provides a Docker Compose configuration that sets up a multi-broker Apache Kafka cluster along with ZooKeeper using Bitnami Docker images. The configuration is designed for local development and testing.

## Overview

The Docker Compose file creates the following services:

- **ZooKeeper**: A single ZooKeeper instance (required by Kafka).
- **Kafka Brokers**: Three Kafka brokers (`kafka1`, `kafka2`, and `kafka3`).

To allow both internal cluster communication and external client connections (e.g., using the Kafka command-line tools), each Kafka broker is configured with **dual listeners**:

- **Internal Listener**  
  - Binds to a container port (e.g. `9092` for `kafka1`).
  - Advertised as the container hostname (e.g. `kafka1:9092`).
  - Used for inter-broker communication within the Docker network.
- **External Listener**  
  - Binds to a different container port that is mapped to the host (e.g. `19092` for `kafka1`).
  - Advertised as `localhost:<external_port>` (e.g. `localhost:19092`).
  - Used for connecting from your host machine.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Setup

1. **Clone the Repository or Copy the Files**  
   Ensure you have the `docker-compose.yaml` file in your working directory.

2. **Start the Cluster**  
   Run the following command in the same directory as your `docker-compose.yaml` file:
   ```bash
   docker-compose up -d
   ```
   This will start ZooKeeper and all three Kafka brokers in detached mode.
   
![Screenshot 2025-02-09 at 2.59.36 AM](https://hackmd.io/_uploads/H19jKQHtkg.png)


3. **Verify the Containers are Running**  
   ```bash
   docker ps
   ```
   You should see the ZooKeeper and Kafka containers running with the appropriate port mappings.
   
![Screenshot 2025-02-09 at 3.00.00 AM](https://hackmd.io/_uploads/rJXTtmHFJl.png)


## Docker Compose Configuration

Below is the complete `docker-compose.yaml` used in this setup:

```yaml
version: '3.8'

services:
  zookeeper:
    image: bitnami/zookeeper:3.8
    container_name: zookeeper
    environment:
      BITNAMI_DEBUG: 'true'
      ALLOW_ANONYMOUS_LOGIN: 'yes'
    ports:
      - "2181:2181"

  kafka1:
    image: bitnami/kafka:3.4
    container_name: kafka1
    depends_on:
      - zookeeper
    environment:
      BITNAMI_DEBUG: 'true'
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      ALLOW_PLAINTEXT_LISTENER: 'yes'
      # Dual listeners for internal and external communication:
      KAFKA_CFG_LISTENERS: INTERNAL://0.0.0.0:9092,EXTERNAL://0.0.0.0:19092
      KAFKA_CFG_ADVERTISED_LISTENERS: INTERNAL://kafka1:9092,EXTERNAL://localhost:19092
      KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP: INTERNAL:PLAINTEXT,EXTERNAL:PLAINTEXT
      KAFKA_CFG_INTER_BROKER_LISTENER_NAME: INTERNAL
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 2
    ports:
      - "19092:19092"

  kafka2:
    image: bitnami/kafka:3.4
    container_name: kafka2
    depends_on:
      - zookeeper
    environment:
      BITNAMI_DEBUG: 'true'
      KAFKA_BROKER_ID: 2
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      ALLOW_PLAINTEXT_LISTENER: 'yes'
      KAFKA_CFG_LISTENERS: INTERNAL://0.0.0.0:9093,EXTERNAL://0.0.0.0:19093
      KAFKA_CFG_ADVERTISED_LISTENERS: INTERNAL://kafka2:9093,EXTERNAL://localhost:19093
      KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP: INTERNAL:PLAINTEXT,EXTERNAL:PLAINTEXT
      KAFKA_CFG_INTER_BROKER_LISTENER_NAME: INTERNAL
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 2
    ports:
      - "19093:19093"

  kafka3:
    image: bitnami/kafka:3.4
    container_name: kafka3
    depends_on:
      - zookeeper
    environment:
      BITNAMI_DEBUG: 'true'
      KAFKA_BROKER_ID: 3
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      ALLOW_PLAINTEXT_LISTENER: 'yes'
      KAFKA_CFG_LISTENERS: INTERNAL://0.0.0.0:9094,EXTERNAL://0.0.0.0:19094
      KAFKA_CFG_ADVERTISED_LISTENERS: INTERNAL://kafka3:9094,EXTERNAL://localhost:19094
      KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP: INTERNAL:PLAINTEXT,EXTERNAL:PLAINTEXT
      KAFKA_CFG_INTER_BROKER_LISTENER_NAME: INTERNAL
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 2
    ports:
      - "19094:19094"
```

## Using the Kafka Cluster

### Creating Topics

Create a topic (for example, `TopicA`) by connecting to the external listeners:
```bash
bin/kafka-topics.sh --create \
  --bootstrap-server localhost:19092,localhost:19093,localhost:19094 \
  --replication-factor 2 \
  --partitions 3 \
  --topic TopicA
```

![Screenshot 2025-02-09 at 3.01.11 AM](https://hackmd.io/_uploads/ry4W5QSFJx.png)


### Listing Topics

List all topics using one of the external listener addresses:
```bash
bin/kafka-topics.sh --list --bootstrap-server localhost:19092
```

### Producing Messages

Send messages to a topic with a producer:
```bash
bin/kafka-console-producer.sh \
  --broker-list localhost:19092,localhost:19093,localhost:19094 \
  --topic TopicA \
  --property parse.key=true \
  --property key.separator=":"
```

![Screenshot 2025-02-09 at 3.02.03 AM](https://hackmd.io/_uploads/rkcE9XrYyl.png)


### Consuming Messages

Consume messages from a topic:
```bash
bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:19092,localhost:19093,localhost:19094 \
  --topic TopicA \
  --from-beginning \
  --property print.key=true \
  --property key.separator=":"
```

![Screenshot 2025-02-09 at 3.02.37 AM](https://hackmd.io/_uploads/BJ9U57Htkx.png)

## Troubleshooting

- **Timeouts or Unknown Host Errors**  
  - Always use the **external** ports (19092, 19093, 19094) when connecting from your host.
  - If you see errors like `UnknownHostException` for `kafka1`, `kafka2`, or `kafka3`, it indicates that the internal hostnames are being advertised instead of the external addresses. Ensure that the `KAFKA_CFG_ADVERTISED_LISTENERS` environment variable is correctly set to use `localhost:<external_port>`.

- **Checking Logs**  
  Use the Docker logs command to check the logs of a specific container:
  ```bash
  docker logs kafka1
  ```

## Shutting Down the Cluster

To stop and remove the containers, run:
```bash
docker-compose down --remove-orphans
```

## Conclusion

This Docker Compose setup provides a convenient way to run a multi-broker Kafka cluster for development and testing. The dual listener configuration ensures that brokers can communicate internally while allowing external clients to seamlessly connect via `localhost`. Adjust the configuration as needed for your environment and happy coding!
