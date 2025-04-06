from pydantic import BaseModel, Field
from typing import List


class MovieBase(BaseModel):
    """Esquema base para filmes."""

    title: str = Field(
        ..., example="The Shawshank Redemption", description="Título do filme"
    )
    genres: List[str] = Field(
        ..., example=["Drama", "Crime"], description="Gêneros do filme"
    )
    director: str = Field(..., example="Frank Darabont", description="Diretor do filme")
    actors: List[str] = Field(
        ...,
        example=["Tim Robbins", "Morgan Freeman"],
        description="Atores principais do filme",
    )


class MovieCreate(MovieBase):
    """Esquema para criação de filmes."""

    class Config:
        schema_extra = {
            "example": {
                "title": "The Godfather",
                "genres": ["Crime", "Drama"],
                "director": "Francis Ford Coppola",
                "actors": ["Marlon Brando", "Al Pacino", "James Caan"],
            }
        }


class MovieResponse(MovieBase):
    """Esquema para resposta com dados de filme."""

    id: str = Field(..., example="60d21b4967d0d8992e610c85", description="ID do filme")

    class Config:
        """Configuração para o modelo Pydantic."""

        from_attributes = True
