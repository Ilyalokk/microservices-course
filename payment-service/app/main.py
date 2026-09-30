from contextlib import asynccontextmanager
import time

from aio_pika import channel
from fastapi import FastAPI, Depends, Request

from app.database import engine
from app.models import Base
from app.dependencies import get_payment_service
from app.rabbitmq import connect_rabbitmq, declare_payment_exchange
from app.schemas import PaymentReadSchema, PaymentCreateSchema
from app.service import PaymentService
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.models import PaymentORM
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    

    connection = await connect_rabbitmq(url=settings.rabbitmq_url)
    channel = await connection.channel()
    app.state.payment_exchange = await declare_payment_exchange(channel, settings.payment_exchange_name)
   
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/payments/{payment_id}", response_model=PaymentReadSchema)
async def get_payment(
    payment_id,
    payment_service: PaymentService = Depends(get_payment_service)
):
    return await payment_service.get(payment_id)


@app.get("/payments", response_model=list[PaymentReadSchema])
async def get_payments(
    payment_service: PaymentService = Depends(get_payment_service)
):
    return await payment_service.get_all()


@app.post(
    "/payments",
    response_model=PaymentReadSchema,
)
async def create_payment(
    request: Request,
    payload: PaymentCreateSchema,
    payment_service: PaymentService = Depends(get_payment_service),
):
    payment = await payment_service.create(payload)

    await payment_service.complete_payment(
        payment,
        order_id=payload.order_id,
        amount=payload.amount,
        exchange=request.app.state.payment_exchange,
    )

    return payment