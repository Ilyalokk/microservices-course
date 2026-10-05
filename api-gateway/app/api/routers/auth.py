from fastapi import APIRouter, Depends, status

from app.api_client import request_service
from app.auth import CurrentUser, get_current_user
from app.config import settings
from app.schemas import TokenResponse, UserLogin, UserRegister


auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@auth_router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    payload: UserRegister,
) -> TokenResponse:
    return await request_service(
        method="POST",
        url=f"{settings.auth_service_url}/register",
        json_body=payload.model_dump(mode="json"),
    )


@auth_router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    payload: UserLogin,
) -> TokenResponse:
    return await request_service(
        method="POST",
        url=f"{settings.auth_service_url}/login",
        json_body=payload.model_dump(mode="json"),
    )


@auth_router.get(
    "/me",
    response_model=CurrentUser,
)
async def get_me(
    user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    return user