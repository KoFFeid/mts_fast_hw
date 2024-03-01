from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError
import re


EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

__all__ = ["IncomingBook", "ReturnedAllBooks", "ReturnedBook"]


# Базовый класс "Продавцы", содержащий поля, которые есть во всех классах-наследниках.
class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    email: str


# Класс для валидации входящих данных. Не содержит id так как его присваивает БД.
class AddedSeller(BaseSeller):

    password: str

    @field_validator("email")  # Валидатор, проверяет что email имеет правильный формат
    @staticmethod
    def validate_mail(val: int):
        if not EMAIL_REGEX.match(val):
             raise PydanticCustomError("Validation error", "Check your email")
        return val


# Класс, валидирующий исходящие данные. Он уже содержит id
class ReturnedSeller(BaseSeller):
    id: int




# Класс для возврата массива объектов "Книга"
class ReturnedAllSellers(BaseModel):
    books: list[ReturnedSeller]
