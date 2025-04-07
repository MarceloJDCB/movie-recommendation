from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import timedelta

from app.dependencies import get_database
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token
from app.utils.auth import get_password_hash, verify_password, create_access_token
from app.config import ACCESS_TOKEN_EXPIRE_DAYS


router = APIRouter(
    prefix="/auth", tags=["auth"], responses={401: {"description": "Não autorizado"}}
)


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar novo usuário",
    description="Cria um novo usuário com senha criptografada e retorna os dados do usuário criado.",
    response_description="Usuário criado com sucesso",
)
async def signup(
    user_data: UserCreate = Body(
        ...,
        example={
            "username": "exemplo_usuario",
            "email": "usuario@exemplo.com",
            "password": "senha123",
        },
    ),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    Cria um novo usuário com senha criptografada.

    - **username**: nome de usuário único
    - **email**: endereço de email válido
    - **password**: senha do usuário (será hashada)

    Retorna os dados do usuário criado (sem a senha).

    Possíveis erros:
    - **400 Bad Request**: Se o nome de usuário ou email já estiverem em uso
    """
    # Verificar se o usuário já existe
    existing_user = await db.users.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário com este nome já existe",
        )

    # Verificar se o email já está em uso
    existing_email = await db.users.find_one({"email": user_data.email})
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Este email já está em uso"
        )

    # Hash da senha
    hashed_password = get_password_hash(user_data.password)

    # Criar novo usuário
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
    )
    user_dict = new_user.to_dict()

    # Inserir no banco de dados
    await db.users.insert_one(user_dict)

    # Remover o campo password_hash antes de retornar
    user_response = {k: v for k, v in user_dict.items() if k != "password_hash"}

    return user_response


@router.post(
    "/login",
    response_model=Token,
    summary="Autenticar usuário",
    description="Autentica um usuário com username e senha e retorna um token JWT de acesso.",
    response_description="Token de acesso JWT",
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    Autentica um usuário e retorna um token JWT.

    - **username**: nome de usuário cadastrado
    - **password**: senha do usuário

    Retorna:
    - **access_token**: Token JWT para autenticação nas APIs protegidas
    - **token_type**: Tipo do token (sempre "bearer")

    Como usar:
    1. Faça uma requisição POST para /auth/login com seu username e password
    2. Receba o token JWT
    3. Use o token nas requisições subsequentes no header Authorization: Bearer {token}

    Possíveis erros:
    - **401 Unauthorized**: Credenciais inválidas
    """
    # Buscar o usuário no banco
    user = await db.users.find_one({"username": form_data.username})
    # Definir a exceção uma única vez
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Nome de usuário ou senha incorretos",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verificar se o usuário existe
    if not user:
        raise credentials_exception

    # Verificar a senha
    if not verify_password(form_data.password, user["password_hash"]):
        raise credentials_exception

    # Gerar token de acesso com expiração de 7 dias
    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        subject=user["username"], expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
