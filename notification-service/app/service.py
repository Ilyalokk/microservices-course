import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import NotificationORM
from .schemas import PaymentSucceededEventSchema


class NotificationService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def handle_payment_succeeded(
        self,
        event: PaymentSucceededEventSchema,
    ) -> NotificationORM:
        stmt = select(NotificationORM).where(
            NotificationORM.event_id == event.event_id
        )

        result = await self.session.scalars(stmt)
        existing_notification = result.first()

        if existing_notification is not None:
            return existing_notification

        notification = NotificationORM(
            event_id=event.event_id,
            order_id=event.order_id,
            event_type="payment.succeeded",
            message=(
                f"Payment for order {event.order_id} "
                f"succeeded. Amount: {event.amount}"
            ),
            status="sent",
            sent_at=datetime.datetime.now(datetime.timezone.utc),
        )

        self.session.add(notification)

        await self.session.commit()
        await self.session.refresh(notification)

        return notification