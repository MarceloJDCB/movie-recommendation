from typing import Optional
from app.models.base_model import BaseModel


class Review(BaseModel):
    """
    Modelo de dados para avaliações de filmes.
    """

    def __init__(
        self,
        user_id: str,
        movie_id: str,
        rating: float,
        comment: Optional[str] = None,
        id: Optional[str] = None,
    ):
        super().__init__()
        self.id = id
        self.user_id = user_id
        self.movie_id = movie_id
        self.rating = rating
        self.comment = comment

    # Métodos to_dict e from_dict herdados da classe base
