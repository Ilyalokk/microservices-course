import json

import aio_pika
from aio_pika.abc import (
    AbstractConnection,
    AbstractIncomingMessage,
    AbstractRobustConnection,
)

from .config import settings
from .database import SessionLocal
from .schemas import PaymentSucceededEventSchema
from .service import NotificationService


async def connect_rabbitmq() -> AbstractRobustConnection:
    return await aio_pika.connect_robust(settings.rabbitmq_url)


async def handle_payment_succeeded(
    message: AbstractIncomingMessage,
) -> None:
    async with message.process():
        event_data = json.loads(message.body.decode("utf-8"))

        event = PaymentSucceededEventSchema.model_validate(event_data)

        async with SessionLocal() as session:
            notification_service = NotificationService(session)

            await notification_service.handle_payment_succeeded(event)


async def start_payment_consume(
    connection: AbstractConnection,
) -> None:
    channel = await connection.channel()

    payment_exchange = await channel.declare_exchange(
        settings.payment_exchange_name
    )

    notification_queue = await channel.declare_queue(
        settings.notification_queue_name
    )

    await notification_queue.bind(
        payment_exchange,
        routing_key=settings.payment_succeeded_routing_key,
    )

    await notification_queue.consume(handle_payment_succeeded)