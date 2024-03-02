import pytest
from fastapi import status
from sqlalchemy import select

from src.models import books, sellers

result = {
    "books": [
        {"author": "fdhgdh", "title": "jdhdj", "year": 1997},
        {"author": "fdhgdfgfrh", "title": "jrrgdhdj", "year": 2001},
    ]
}


# Тест на ручку создающую продавца
@pytest.mark.asyncio
async def test_create_seller(async_client):

    data = {"first_name": "Pedro", "last_name": "Paskal",
             "email": "my_new_email@yandex.ru", "password":"2007"}
    
    response = await async_client.post("/api/v1/seller/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    assert result_data == {
        "id": result_data["id"],
        "first_name": "Pedro",
        "last_name": "Paskal",
        "email": "my_new_email@yandex.ru"
    }


# Тест на ручку получения списка продавцов
@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):

    seller1 = sellers.Seller(first_name="Pushkin", last_name="Eugeny Onegin",
                       email="VP@yandex.ru", password="valerii1234")
    
    seller2 = sellers.Seller(first_name="Petr", last_name="Petrov",
                       email="PP@yandex.ru", password="Petr1234")
    db_session.add_all([seller1, seller2])
    await db_session.flush()

    response = await async_client.get("/api/v1/seller/")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "sellers": [
            {"first_name": "Pushkin", "last_name": "Eugeny Onegin", "email": "VP@yandex.ru",
              "id": seller1.id},
            {"first_name": "Petr", "last_name": "Petrov", "email": "PP@yandex.ru",
              "id": seller2.id},
        ]
    }


# Тест на ручку получения продавца со списком книг
@pytest.mark.asyncio
async def test_get_single_seller(db_session, async_client):

    seller = sellers.Seller(first_name="Pushkin", last_name="EugenyOnegin",
                       email="VP@yandex.ru", password="valerii1234")
    db_session.add(seller)
    await db_session.flush()


    book = books.Book(author="Pushkin", title="Eugeny Onegin",
                       year=2001, count_pages=104, seller_id=seller.id)
    book2 = books.Book(author="Pushkin", title="Eugeny Onegin2",
                       year=2001, count_pages=103, seller_id=seller.id)
    db_session.add_all([book, book2])

    await db_session.flush()

    response = await async_client.get(f"/api/v1/seller/{seller.id}")

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["books"]) == 2

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json()["books"][0] == {
        "title": "Eugeny Onegin",
        "author": "Pushkin",
        "year": 2001,
        "count_pages": 104,
        "id": book.id,
        "seller_id": seller.id
    }


# Тест на ручку удаления продавца
@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):

    seller = sellers.Seller(first_name="Pushkin", last_name="Eugeny Onegin",
                       email="VP@yandex.ru", password="valerii1234")
    
    db_session.add(seller)
    await db_session.flush()

    book = books.Book(author="Pushkin", title="Eugeny Onegin",
                       year=2001, count_pages=104, seller_id=seller.id)

    db_session.add(book)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/seller/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()


    seller_book = await db_session.get(books.Book, book.id)
    seller = await db_session.get(sellers.Seller, seller.id)
    assert seller is None and seller_book is None           # Если продавец и книга отсутсвуют, то ручка работает правильно


# Тест на ручку обновления продавцы
@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке

    seller = sellers.Seller(first_name="Pushkin", last_name="Eugeny Onegin",
                       email="VP@yandex.ru", password="valerii1234")
    
    db_session.add(seller)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/seller/{seller.id}",
        json={      "first_name": "Maximilian",
                    "last_name": "Kolotushkin",
                    "email": "MK@yandex.ru",
                    "id":seller.id},
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(sellers.Seller, seller.id)
    assert res.first_name == "Maximilian"
    assert res.last_name == "Kolotushkin"
    assert res.email == "MK@yandex.ru"
    assert res.id == seller.id
