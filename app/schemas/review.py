from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ReviewBase(BaseModel):
    """Esquema base para avaliações."""

    movie_id: str = Field(
        ..., example="60d21b4967d0d8992e610c86", description="ID do filme avaliado"
    )
    rating: float = Field(..., ge=0, le=5, example=4.5, description="Nota de 0 a 5")
    comment: Optional[str] = Field(
        None,
        example="Excelente filme!",
        description="Comentário opcional sobre o filme",
    )


class UserReviewBase(ReviewBase):
    """Esquema base para avaliações com ID do usuário (para uso interno)."""

    user_id: str = Field(
        ...,
        example="60d21b4967d0d8992e610c85",
        description="ID do usuário que fez a avaliação",
    )


class ReviewCreate(ReviewBase):
    """Esquema para criação de avaliações."""

    class Config:
        schema_extra = {
            "example": {
                "movie_id": "60d21b4967d0d8992e610c86",
                "rating": 4.5,
                "comment": "Um dos melhores filmes que já vi!",
            }
        }


class ReviewResponse(UserReviewBase):
    """Esquema para resposta com dados de avaliação."""

    id: str = Field(
        ..., example="60d21b4967d0d8992e610c87", description="ID da avaliação"
    )
    created_at: datetime = Field(
        ..., example="2023-01-15T14:30:00", description="Data de criação da avaliação"
    )

    class Config:
        """Configuração para o modelo Pydantic."""

        from_attributes = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}
