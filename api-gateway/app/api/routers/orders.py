from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.api_client import request_service
from app.auth import CurrentUser, get_current_user
from app.config import settings
from app.schemas import OrderCreate


orders_router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)


@orders_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_order(
    payload: OrderCreate,
    user: CurrentUser = Depends(get_current_user),
) -> Any:
    order_payload = payload.model_dump(mode="json")

    order_payload["user_id"] = user.id

    return await request_service(
        method="POST",
        url=f"{settings.order_service_url}/orders",
        json_body=order_payload,
    )


@orders_router.get("/{order_id}")
async def get_order(
    order_id: str,
    user: CurrentUser = Depends(get_current_user),
) -> Any:
    order = await request_service(
        method="GET",
        url=f"{settings.order_service_url}/orders/{order_id}",
    )

    ensure_order_owner(
        order=order,
        user=user,
    )

    return order


def ensure_order_owner(
    order: Any,
    user: CurrentUser,
) -> None:
    if (
        not isinstance(order, dict)
        or order.get("user_id") != user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )