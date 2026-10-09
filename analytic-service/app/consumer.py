import json

from aiokafka import AIOKafkaConsumer, ConsumerRecord

from .config import settings


async def save_event(collection, message: ConsumerRecord):
    event = json.loads(message.value.decode("utf-8"))

    print(f"Received Kafka event: {event}")

    await collection.insert_one(event)


async def consume_events(collection):
    consumer = AIOKafkaConsumer(
        settings.kafka_topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id="analytics-service",
        auto_offset_reset="earliest",
    )

    await consumer.start()

    print("Analytics Kafka consumer started")

    try:
        async for message in consumer:
            await save_event(collection, message)
    finally:
        await consumer.stop()