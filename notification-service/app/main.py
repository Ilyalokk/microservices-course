from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import engine
from app.models import Base
from app.rabbitmq import connect_rabbitmq, start_payment_consume


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаём таблицы Notification Service
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    # Подключаемся к RabbitMQ
    rabbitmq_connection = await connect_rabbitmq()

    # Подписываем Notification Service на payment.succeeded
    await start_payment_consume(rabbitmq_connection)

    # Сохраняем connection, чтобы оно жило всё время работы приложения
    app.state.rabbitmq_connection = rabbitmq_connection

    yield

    # При остановке приложения закрываем соединение
    await rabbitmq_connection.close()


app = FastAPI(
    title="Notification Service",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    return {
        "service": "notification-service",
        "status": "ok",
    }