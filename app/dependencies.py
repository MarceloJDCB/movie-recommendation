from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import Dict, Any
from datetime import datetime

from app.config import MONGO_URL, DATABASE_NAME
from app.config import JWT_SECRET_KEY, JWT_ALGORITHM
from app.schemas.user import TokenPayload

# Cliente MongoDB assíncrono
client = AsyncIOMotorClient(MONGO_URL)
db = client[DATABASE_NAME]

# OAuth2 scheme para autenticação via Bearer token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# Dependência para injetar o banco de dados nas rotas
async def get_database() -> AsyncIOMotorDatabase:
    """
    Retorna a instância do banco de dados para ser injetada nas rotas.
    Esta função é utilizada como dependência no FastAPI.
    """
    return db


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Dict[str, Any]:
    """
    Dependência para obter o usuário atual a partir do token JWT.
    Usada para proteger rotas que requerem autenticação.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais de autenticação inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception

        token_data = TokenPayload(**payload)

        # Verificar expiração
        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise credentials_exception

    # Buscar o usuário no banco
    user = await db.users.find_one({"username": username})
    if user is None:
        raise credentials_exception

    return user
