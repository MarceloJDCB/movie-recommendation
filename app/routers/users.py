from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict, Any

from app.dependencies import get_database, get_current_user
from app.schemas.user import UserResponse

# Criação do roteador para o módulo de usuários
router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={
        404: {"description": "Não encontrado"},
        401: {"description": "Não autorizado - Token inválido ou expirado"},
    },
)


@router.get(
    "/",
    response_model=List[UserResponse],
    summary="Listar todos os usuários",
    description="Retorna uma lista paginada de todos os usuários registrados no sistema.",
    response_description="Lista de usuários",
)
async def list_users(
    skip: int = 0, limit: int = 100, db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Retorna uma lista de usuários.

    - **skip**: número de registros para pular (paginação)
    - **limit**: número máximo de registros para retornar

    Esta rota não requer autenticação.
    """
    users = await db.users.find().skip(skip).limit(limit).to_list(length=limit)
    return users


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obter dados do usuário atual",
    description="Retorna os dados do usuário autenticado pelo token JWT.",
    response_description="Dados do usuário autenticado",
)
async def get_user_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Retorna os dados do usuário autenticado.

    Esta rota requer autenticação via Bearer token.

    Para usar:
    1. Faça login com /auth/login para obter um token
    2. Envie o token no header Authorization: Bearer {token}
    3. Receba os dados do seu próprio usuário

    Possíveis erros:
    - **401 Unauthorized**: Token inválido, expirado ou ausente
    """
    return current_user
