import jwt
from datetime import datetime, timedelta
import bcrypt

from src.configurations.settings import settings

SECRET_KEY = settings.token_secret_key
ALGORITHM = settings.token_secret_key
EXPIRATION_TIME = timedelta(minutes=settings.access_token_expire_minutes)


def create_jwt_token(email):
    expiration = datetime.utcnow() + EXPIRATION_TIME

    payload = {
        "user_email": email,
        "expires": expiration
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return token
    

def verify_jwt_token(token: str):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_token if decoded_token["expires"] >= datetime.utcnow() else None
    except jwt.PyJWTError:
        return None
        

def get_hashed_password(password: str) -> str: # Хэширование пароля
    return bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, hashed_pass: str) -> bool:   # Проверяет правильность введенного пароля
    return bcrypt.checkpw(password, hashed_pass)