from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """Esquema base para usuários."""

    username: str = Field(..., example="john_doe", description="Nome de usuário único")
    email: EmailStr = Field(
        ..., example="john@example.com", description="Email do usuário"
    )


class UserAuth(UserBase):
    """Esquema para autenticação de usuários."""

    password: str = Field(
        ...,
        min_length=6,
        example="password123",
        description="Senha de acesso (mínimo de 6 caracteres)",
    )


class UserCreate(UserAuth):
    """Esquema para criação de usuários."""

    class Config:
        schema_extra = {
            "example": {
                "username": "novo_usuario",
                "email": "usuario@exemplo.com",
                "password": "senha123",
            }
        }


class UserResponse(UserBase):
    """Esquema para resposta com dados de usuário."""

    created_at: datetime = Field(
        ..., example="2023-01-15T14:30:00", description="Data de criação do usuário"
    )

    class Config:
        """Configuração para o modelo Pydantic."""

        from_attributes = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}
        schema_extra = {
            "example": {
                "username": "usuario_exemplo",
                "email": "usuario@exemplo.com",
                "created_at": "2023-01-15T14:30:00",
            }
        }


class Token(BaseModel):
    """Esquema para tokens de autenticação."""

    access_token: str = Field(
        ...,
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        description="Token JWT de acesso",
    )
    token_type: str = Field(
        ..., example="bearer", description="Tipo do token (sempre 'bearer')"
    )

    class Config:
        schema_extra = {
            "example": {
                "access_token": """
                eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c3VhcmlvX2V4ZW1wbG8iLCJleHAiOjE3MDIyMzQ1Njd9.token_signature
                """,
                "token_type": "bearer",
            }
        }


class TokenPayload(BaseModel):
    """Esquema para payload do token JWT."""

    sub: Optional[str] = Field(
        None, example="username", description="Identificador do usuário (username)"
    )
    exp: Optional[int] = Field(
        None, example=1702234567, description="Timestamp de expiração do token"
    )
