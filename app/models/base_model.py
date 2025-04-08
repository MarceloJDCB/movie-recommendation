from typing import Dict, Any, ClassVar
from datetime import datetime
from bson import ObjectId


class BaseModel:
    """
    Classe base para modelos de dados que serão armazenados no MongoDB.

    Fornece funcionalidades comuns como conversão de/para dicionários
    e manipulação de identificadores.
    """

    # Campos que serão excluídos na serialização para dicionário
    _exclude_fields: ClassVar[list] = []

    def __init__(self):
        self.created_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """
        Converte o objeto para um dicionário que pode ser salvo no MongoDB.
        """
        # Começamos com um dicionário das variáveis de instância
        result = {}

        # Para cada atributo que não começa com _ e não está excluído
        for key, value in self.__dict__.items():
            if not key.startswith("_") and key not in self._exclude_fields:
                result[key] = value

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """
        Cria uma instância da classe a partir de um
        dicionário recuperado do MongoDB.
        """
        instance = cls.__new__(cls)

        # Processar o ID do MongoDB se presente
        if "_id" in data and hasattr(cls, "id"):
            instance.id = str(data["_id"])

        # Atribuir todos os outros campos diretamente
        for key, value in data.items():
            if key != "_id":  # Ignorar _id pois já foi processado
                setattr(instance, key, value)

        return instance

    @staticmethod
    def ensure_object_id(id_value: str) -> ObjectId:
        """
        Converte uma string em ObjectId, garantindo sua validade.
        """
        try:
            return ObjectId(id_value)
        except Exception:
            raise ValueError(f"ID inválido: {id_value}")
