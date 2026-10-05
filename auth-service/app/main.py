from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, engine
from app.dependencies import get_current_user
from app.schemas import TokenResponse, UserRead, UserRegister, UserLogin
from app.models import Base, User
from app.security import (
    hash_password,
    verify_password,
    created_access_token,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield


app = FastAPI(lifespan=lifespan)


@app.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,

)
async def register(
    payload: UserRegister,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    existing_user = await db.scalar(
        select(User).where(User.email == str(payload.email))
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    user = User(
        email=str(payload.email),
        password_hash=hash_password(payload.password),
    )

    db.add(user)

    await db.commit()
    await db.refresh(user)

    access_token = created_access_token(user)

    return TokenResponse(
        access_token=access_token,
        user=UserRead.model_validate(user),
    )


@app.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    payload: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    user = await db.scalar(
        select(User).where(
            User.email == str(payload.email)
        )
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(
        payload.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = created_access_token(user)

    return TokenResponse(
        access_token=access_token,
        user=UserRead.model_validate(user),
    )

@app.get(
    "/me",
    response_model=UserRead,
)
async def get_me(
    user: User = Depends(get_current_user),
) -> UserRead:
    return UserRead.model_validate(user)