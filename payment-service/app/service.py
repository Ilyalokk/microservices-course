import asyncio

from sqlalchemy import select

from aio_pika.abc import AbstractExchange
from aiokafka import AIOKafkaProducer
from sqlalchemy.ext.asyncio import AsyncSession

from .config import NotFoundError, settings
from .models import PaymentORM
from .rabbitmq import event_publish_json
from .schemas import PaymentCreateSchema, PaymentReadSchema
from .kafka import publish_kafka_event
from .events import build_payment_succeeded_event


class PaymentService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        payment_data: PaymentCreateSchema,
    ) -> PaymentORM:
        payment = PaymentORM(
            order_id=payment_data.order_id,
            status="created",
            amount=payment_data.amount,
        )

        self.session.add(payment)
        await self.session.commit()
        await self.session.refresh(payment)

        return payment

    async def get(self, payment_id: str) -> PaymentORM:
        payment = await self.session.get(PaymentORM, payment_id)

        if payment is None:
            raise NotFoundError

        return payment

    async def get_all(self):
        stmt = select(PaymentORM)
        result = await self.session.scalars(stmt)
        return list(result.all())

    async def complete_payment(
        self,
        payment: PaymentORM,
        order_id: str,
        amount: int,
        exchange: AbstractExchange,
        kafka_producer: AIOKafkaProducer,
    ):
        await asyncio.sleep(4)

        payment.status = "succeeded"
        await self.session.commit()

        event = build_payment_succeeded_event(
            payment_id=payment.id, 
            order_id=order_id, 
            amount=amount
        )

        await event_publish_json(
            exchange,
            settings.payment_succeeded_routing_key,
            data=event,
        )

        await publish_kafka_event(kafka_producer, settings.kafka_analytic_payment_topic, event)

        return PaymentReadSchema.model_validate(payment)