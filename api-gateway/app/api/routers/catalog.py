from typing import Any

from fastapi import APIRouter

from app.api_client import request_service
from app.config import settings


catalog_router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@catalog_router.get("")
async def get_products() -> Any:
    return await request_service(
        method="GET",
        url=f"{settings.catalog_service_url}/products",
    )


@catalog_router.get("/{product_id}")
async def get_product(
    product_id: str,
) -> Any:
    return await request_service(
        method="GET",
        url=f"{settings.catalog_service_url}/products/{product_id}",
    )