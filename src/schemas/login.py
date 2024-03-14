from pydantic import BaseModel

__all__ = ["LoginSchema"]


# Класс для получения токена
class LoginSchema(BaseModel):
    email: str
    password: str