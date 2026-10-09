import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI

from app.consumer import consume_events
from app.database import events_collection, mongodb_client


def log_task_result(task: asyncio.Task):
    if task.cancelled():
        return

    exception = task.exception()

    if exception:
        print(f"Analytics consumer crashed: {exception!r}")


@asynccontextmanager
async def lifespan(_: FastAPI):
    task = asyncio.create_task(
        consume_events(events_collection)
    )

    task.add_done_callback(log_task_result)

    try:
        yield
    finally:
        task.cancel()

        with suppress(asyncio.CancelledError):
            await task

        await mongodb_client.close()


app = FastAPI(lifespan=lifespan)


@app.get("/events")
async def get_events(limit: int = 20):
    query = (
        events_collection
        .find()
        .sort("create_at", -1)
        .limit(limit)
    )

    return await query.to_list(length=limit)