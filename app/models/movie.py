from typing import List, Optional
from app.models.base_model import BaseModel


class Movie(BaseModel):
    """
    Modelo de dados para filmes.
    """

    def __init__(
        self,
        title: str,
        genres: List[str],
        director: str,
        actors: List[str],
        id: Optional[str] = None,
    ):
        super().__init__()
        self.id = id
        self.title = title
        self.genres = genres
        self.director = director
        self.actors = actors

    # Methods to_dict and from_dict are inherited from BaseModel

    def to_mongo(self):
        """
        Converte o objeto para um formato compatível com MongoDB,
        excluindo o campo 'id'.
        """
        data = self.to_dict()
        if "id" in data:
            del data["id"]
        return data

    @classmethod
    def from_mongo(cls, data: dict):
        """
        Cria uma instância de Movie a partir de um documento do MongoDB.
        Converte o campo '_id' para 'id'.
        """
        if "_id" in data:
            id_str = str(data.pop("_id"))
            return cls(
                id=id_str,
                title=data.get("title", ""),
                genres=data.get("genres", []),
                director=data.get("director", ""),
                actors=data.get("actors", []),
            )
        return cls(
            title=data.get("title", ""),
            genres=data.get("genres", []),
            director=data.get("director", ""),
            actors=data.get("actors", []),
        )
