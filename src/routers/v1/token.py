from http.client import HTTPException
from typing import Annotated
from fastapi import APIRouter, Depends, Response, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.configurations.database import get_async_session
from src.models.sellers import Seller
from src.schemas.login import LoginSchema

from src.utils.auth_utils import verify_password, create_jwt_token


token_router = APIRouter(tags=["token"], prefix="/token")

DBSession = Annotated[AsyncSession, Depends(get_async_session)]


@token_router.post("/")
async def add_token(login_data: LoginSchema, session: DBSession):
    user = await session.execute(
        select(Seller).where(Seller.email == login_data.email)
    ).scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email wasn't found")
    
    if not verify_password(login_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong email or password")

    return create_jwt_token(user.email)
