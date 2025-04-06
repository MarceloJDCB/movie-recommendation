from typing import List, Dict, Any, TypeVar, Generic, Type, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, status

from app.models.base_model import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseRepository(Generic[T]):
    """
    Repositório base para operações CRUD com MongoDB.
    """

    def __init__(
        self, db: AsyncIOMotorDatabase, collection_name: str, model_class: Type[T]
    ):
        self.collection = db[collection_name]
        self.model_class = model_class

    async def find_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Retorna todos os documentos da coleção com paginação."""
        cursor = self.collection.find().skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)
        return [self._process_document(doc) for doc in documents]

    async def find_one(self, id: str) -> Optional[T]:
        """Busca um documento pelo ID."""
        try:
            obj_id = ObjectId(id)
            document = await self.collection.find_one({"_id": obj_id})
            if document:
                return self._process_document(document)
            return None
        except Exception:
            return None

    async def find_by_field(self, field: str, value: Any) -> List[T]:
        """Busca documentos por um campo específico."""
        cursor = self.collection.find({field: value})
        documents = await cursor.to_list(length=100)
        return [self._process_document(doc) for doc in documents]

    async def create(self, model: T) -> T:
        """Cria um novo documento na coleção."""
        document = model.to_dict()
        result = await self.collection.insert_one(document)
        created = await self.collection.find_one({"_id": result.inserted_id})
        return self._process_document(created)

    async def exists(self, id: str) -> bool:
        """Verifica se um documento existe pelo ID."""
        try:
            obj_id = ObjectId(id)
            count = await self.collection.count_documents({"_id": obj_id})
            return count > 0
        except Exception:
            return False

    async def validate_existence(
        self, id: str, error_message: str = "Item não encontrado"
    ):
        """Valida a existência de um documento ou lança uma exceção."""
        exists = await self.exists(id)
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=error_message
            )

    def _process_document(self, document: Dict[str, Any]) -> T:
        """Processa um documento do MongoDB para objeto do modelo."""
        if document is None:
            return None

        # Converter _id para string
        document["id"] = str(document["_id"])

        # Criar a instância do modelo usando from_dict
        return self.model_class.from_dict(document)
