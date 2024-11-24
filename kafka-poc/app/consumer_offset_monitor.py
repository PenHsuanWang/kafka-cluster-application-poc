# consumer_offset_monitor.py

from kafka import KafkaAdminClient, KafkaConsumer
from kafka.structs import TopicPartition
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError
import json
import argparse
import sys

def list_topics(bootstrap_servers):
    try:
        admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers, client_id='offset-monitor')
        topics = admin_client.list_topics()
        admin_client.close()
        return topics
    except Exception as e:
        print(f"Error listing topics: {e}")
        sys.exit(1)

def create_topic(bootstrap_servers, topic_name, num_partitions=1, replication_factor=1):
    try:
        admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers, client_id='offset-monitor')
        topic_list = [NewTopic(name=topic_name, num_partitions=num_partitions, replication_factor=replication_factor)]
        admin_client.create_topics(new_topics=topic_list, validate_only=False)
        print(f"Topic '{topic_name}' created.")
    except TopicAlreadyExistsError:
        print(f"Topic '{topic_name}' already exists.")
    except Exception as e:
        print(f"Failed to create topic '{topic_name}': {e}")
    finally:
        admin_client.close()

def monitor_consumer_group(bootstrap_servers, group_id):
    try:
        admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers, client_id='offset-monitor')
        consumer_groups = admin_client.describe_consumer_groups([group_id])
        admin_client.close()

        if not consumer_groups:
            print(f"Consumer group '{group_id}' does not exist.")
            sys.exit(1)

        group_description = consumer_groups[0]  # Assuming single group_id is provided

        # Debugging: Print type and attributes
        print(f"Type of group_description: {type(group_description)}")
        print(f"Attributes of group_description: {dir(group_description)}\n")

        # Accessing attributes based on kafka-python's GroupInformation
        print(f"Group: {group_description.group}")  # Corrected from group_id to group
        print(f"State: {group_description.state}")
        print(f"Protocol: {group_description.protocol}")
        print(f"Protocol Type: {group_description.protocol_type}")
        print(f"Members:")
        print(f"{'CONSUMER-ID':<50} {'HOST':<20} {'CLIENT-ID':<20}")
        print('-' * 90)
        for member in group_description.members:
            consumer_id = member.consumer_id
            host = member.client_host  # Correct attribute name
            client_id = member.client_id
            print(f"{consumer_id:<50} {host:<20} {client_id:<20}")
        
        print("\nOffsets:")
        print(f"{'TOPIC':<20} {'PARTITION':<10} {'CURRENT-OFFSET':<15} {'LOG-END-OFFSET':<15} {'LAG':<10}")
        print('-' * 70)

        # Create a consumer to fetch committed and end offsets
        consumer = KafkaConsumer(
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            enable_auto_commit=False,
            auto_offset_reset='earliest',
            consumer_timeout_ms=1000  # Prevents hanging if no messages are present
        )

        # Collect all topic-partitions assigned to the group
        topic_partitions = []
        for member in group_description.members:
            for assignment in member.assignment.topic_partitions:
                tp = TopicPartition(assignment.topic, assignment.partition)
                if tp not in topic_partitions:
                    topic_partitions.append(tp)

        if not topic_partitions:
            print(f"No partitions assigned to consumer group '{group_id}'.")
            consumer.close()
            return

        consumer.assign(topic_partitions)

        # Fetch committed offsets
        committed_offsets = consumer.committed(topic_partitions)

        # Fetch end offsets
        end_offsets = consumer.end_offsets(topic_partitions)

        for tp in topic_partitions:
            committed = committed_offsets.get(tp)
            end = end_offsets.get(tp)
            if committed is not None:
                lag = end - committed
            else:
                lag = 'N/A'
            print(f"{tp.topic:<20} {tp.partition:<10} {committed if committed is not None else 'None':<15} {end:<15} {lag:<10}")

        consumer.close()

    except AttributeError as ae:
        print(f"Attribute error: {ae}")
        print("Please ensure you are using the latest version of kafka-python.")
        sys.exit(1)
    except Exception as e:
        print(f"Error monitoring consumer group: {e}")
        sys.exit(1)

def fetch_latest_n_events(bootstrap_servers, topic, n):
    try:
        consumer = KafkaConsumer(
            bootstrap_servers=bootstrap_servers,
            enable_auto_commit=False,
            auto_offset_reset='latest',
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
            consumer_timeout_ms=1000  # Prevents hanging if no messages are present
        )

        partitions = consumer.partitions_for_topic(topic)
        if partitions is None:
            print(f"Topic '{topic}' does not exist.")
            consumer.close()
            return []

        topic_partitions = [TopicPartition(topic, p) for p in partitions]
        consumer.assign(topic_partitions)

        latest_events = []

        for tp in topic_partitions:
            end_offset = consumer.end_offsets([tp])[tp]
            start_offset = max(end_offset - n, 0)
            consumer.seek(tp, start_offset)

            while True:
                msg_pack = consumer.poll(timeout_ms=1000, max_records=100)
                if not msg_pack:
                    break
                for records in msg_pack.values():
                    for message in records:
                        latest_events.append({
                            "topic": message.topic,
                            "partition": message.partition,
                            "offset": message.offset,
                            "key": message.key,
                            "value": message.value,
                            "timestamp": message.timestamp
                        })
                        if len(latest_events) >= n:
                            break
                    if len(latest_events) >= n:
                        break
                if len(latest_events) >= n:
                    break

        consumer.close()
        return latest_events
    except Exception as e:
        print(f"Error fetching latest events: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Kafka Consumer Offset Monitor')
    parser.add_argument('--bootstrap-servers', required=True, nargs='+', help='Kafka bootstrap servers (e.g., localhost:9092)')
    parser.add_argument('--topic', help='Kafka topic')
    parser.add_argument('--group-id', help='Consumer group ID')
    parser.add_argument('--num-events', type=int, default=5, help='Number of latest events to fetch')

    args = parser.parse_args()

    bootstrap_servers = args.bootstrap_servers
    topic = args.topic
    group_id = args.group_id
    n = args.num_events

    # If topic and group_id are provided, monitor the consumer group and fetch latest events
    if topic and group_id:
        # Create the topic if it doesn't exist
        create_topic(bootstrap_servers, topic)

        # List all topics
        topics = list_topics(bootstrap_servers)
        print(f"Available topics: {topics}\n")

        # Monitor consumer group offsets
        monitor_consumer_group(bootstrap_servers, group_id)

        # Fetch latest N events
        latest_events = fetch_latest_n_events(bootstrap_servers, topic, n)
        if latest_events:
            print(f"\nLatest {n} events from topic '{topic}':")
            for event in latest_events:
                print(event)
        else:
            print(f"No events found in topic '{topic}'.")
    elif group_id:
        # If only group_id is provided, monitor the consumer group without topic
        monitor_consumer_group(bootstrap_servers, group_id)
    else:
        print("Please provide at least --group-id to monitor a consumer group.")
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()