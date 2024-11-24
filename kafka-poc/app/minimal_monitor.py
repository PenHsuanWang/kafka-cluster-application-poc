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
        print(f"Group ID: {group_description.group_id}")
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