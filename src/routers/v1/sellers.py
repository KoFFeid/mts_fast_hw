from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from icecream import ic
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.models.books import Book
from src.models.sellers import Seller
from src.schemas import ReturnedSeller, AddedSeller, ReturnedAllSellers, ReturnedSellerWithBooks
import bcrypt


sellers_router = APIRouter(tags=["seller "], prefix="/seller")

# Больше не симулируем хранилище данных. Подключаемся к реальному, через сессию.
DBSession = Annotated[AsyncSession, Depends(get_async_session)]


# Ручка для создания регистрации продавца в системе. 
@sellers_router.post("/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED)  # Прописываем модель ответа
async def add_seller(
    seller: AddedSeller, session: DBSession
):  # прописываем модель валидирующую входные данные и сессию как зависимость.
    # это - бизнес логика. Обрабатываем данные, сохраняем, преобразуем и т.д.

    new_seller = Seller(        
        first_name=seller.first_name,
        last_name=seller.last_name,
        email=seller.email,
        password=bcrypt.hashpw(seller.password.encode('utf-8'),
                                bcrypt.gensalt()).decode('utf8')
        )
    
    session.add(new_seller)
    await session.flush()

    return new_seller


# Ручка, возвращающая всех продавцов
@sellers_router.get("/", response_model=ReturnedAllSellers)
async def get_all_books(session: DBSession):
    query = select(Seller)
    res = await session.execute(query)
    sellers = res.scalars().all()
    return {"sellers": sellers}


# Ручка для получения продавца со списком книг
@sellers_router.get("/{seller_id}", response_model=ReturnedSellerWithBooks)
async def get_seller(seller_id: int, session: DBSession):
    res = await session.execute(
        select(Seller).where(Seller.id == seller_id).options(selectinload(Seller.books))
    )
    seller = res.scalar_one_or_none()
    return seller


# Ручка для обновления данных о продавце
@sellers_router.put("/{seller_id}", response_model=ReturnedSeller)
async def update_seller(seller_id: int, new_data: ReturnedSeller, session: DBSession):
    # Оператор "морж", позволяющий одновременно и присвоить значение и проверить его.
    if updated_seller := await session.get(Seller, seller_id):
        updated_seller.first_name=new_data.first_name
        updated_seller.last_name=new_data.last_name
        updated_seller.email=new_data.email
        await session.flush()

        return updated_seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)


# Ручка для удаления продавца
@sellers_router.delete("/{seller_id}")
async def delete_seller(seller_id: int, session: DBSession):
    deleted_seller = await session.get(Seller, seller_id)
    ic(deleted_seller)  # Красивая и информативная замена для print. Полезна при отладке.
    if deleted_seller:
        await session.delete(deleted_seller)

    return Response(status_code=status.HTTP_204_NO_CONTENT)  # Response может вернуть текст и метаданные.


