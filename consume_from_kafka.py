from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
import time
import os


def main():
    sr_client = SchemaRegistryClient({"url": "http://127.0.0.1:8081"})

    deserializer = AvroDeserializer(sr_client)

    config = {
        "bootstrap.servers": "127.0.0.1:29092",
        "group.id": "pyconsumer4",
        "value.deserializer": deserializer,
        "auto.offset.reset": "earliest"
    }
    consumer = DeserializingConsumer(config)

    consumer.subscribe(["ace.ace_shard.biota_properties_int"])

    while True:
        msg = consumer.poll(1)
        if msg is None:
            print("waiting for messages...")
            time.sleep(1)
        else:
            deserialized = msg.value()
            print(deserialized)


if __name__ == "__main__":
    main()
