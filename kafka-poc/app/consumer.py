# consumer.py

from kafka import KafkaConsumer
import json

def consume_messages(bootstrap_servers, topic, group_id):
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=group_id,
        enable_auto_commit=True,
        auto_offset_reset='earliest',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        key_deserializer=lambda k: k.decode('utf-8') if k else None
    )

    print(f"Consuming messages from topic '{topic}' in group '{group_id}'...")
    try:
        for message in consumer:
            print(f"Consumed message: {message.value}")
    except KeyboardInterrupt:
        print("Consumer stopped.")
    finally:
        consumer.close()

if __name__ == "__main__":
    bootstrap_servers = ['localhost:9092']
    topic = 'sample-topic'
    group_id = 'sample-consumer-group'
    consume_messages(bootstrap_servers, topic, group_id)