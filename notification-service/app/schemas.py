import datetime

from pydantic import BaseModel, ConfigDict


class PaymentSucceededEventSchema(BaseModel):
    event_id: str
    order_id: str
    status: str
    amount: int


class NotificationReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    event_id: str
    order_id: str
    event_type: str
    message: str
    status: str
    created_at: datetime.datetime
    sent_at: datetime.datetime | None