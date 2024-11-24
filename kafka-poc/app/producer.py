from kafka import KafkaProducer
import json
import time
import random

def produce_messages(bootstrap_servers, topic, num_messages=10):
    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        key_serializer=lambda k: k.encode('utf-8') if k else None
    )

    for i in range(num_messages):
        message = {
            "id": i + 1,
            "timestamp": int(time.time() * 1000),
            "value": random.randint(0, 100),
            "message": f"Sample message {i + 1}"
        }
        key = f"key-{i + 1}"
        producer.send(topic, key=key, value=message)
        print(f"Produced message to topic '{topic}': {message}")
        time.sleep(0.5)

    producer.flush()
    producer.close()

if __name__ == "__main__":
    bootstrap_servers = ['localhost:9092']
    topic = 'sample-topic'
    produce_messages(bootstrap_servers, topic)