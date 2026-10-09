import json

from aiokafka import AIOKafkaProducer

from .config import settings


def create_kafka_producer() -> AIOKafkaProducer:
    return AIOKafkaProducer(bootstrap_servers=settings.kafka_bootstrap_servers)

async def publish_kafka_event(
        producer: AIOKafkaProducer, 
        topic: str, 
        event: dict
    ) -> None:
    payload = json.dumps(event).encode("utf-8")
    return await producer.send_and_wait(topic, value=payload)