from typing import Optional
from app.models.base_model import BaseModel


class User(BaseModel):
    """
    Modelo de dados para usuários.
    """

    def __init__(self, username: str, email: str, password_hash: Optional[str] = None):
        super().__init__()
        self.username = username
        self.email = email
        self.password_hash = password_hash

    # Os métodos to_dict e from_dict agora vêm da classe base
    # Podemos sobrescrever apenas se precisarmos de comportamentos específicos
