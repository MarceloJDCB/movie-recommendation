from typing import Dict, Any
import re
from bson import ObjectId


def validate_object_id(id_value: str) -> bool:
    """
    Verifica se uma string é um ObjectId MongoDB válido.

    Args:
        id_value: String a ser validada

    Returns:
        True se for um ObjectId válido, False caso contrário
    """
    try:
        ObjectId(id_value)
        return True
    except Exception:
        return False


def validate_email(email: str) -> bool:
    """
    Valida se uma string é um email em formato válido.

    Utiliza uma expressão regular para verificar o formato básico do email.
    Não garante que o email existe, apenas que o formato é válido.

    Args:
        email: String contendo o email a ser validado

    Returns:
        True se o formato for válido, False caso contrário
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Verifica a força da senha baseado em critérios comuns.

    Critérios:
    - Pelo menos 8 caracteres
    - Contém letra maiúscula
    - Contém letra minúscula
    - Contém número
    - Contém caractere especial

    Args:
        password: Senha a ser validada

    Returns:
        Dicionário com resultado da validação e mensagem
    """
    if len(password) < 8:
        return {"valid": False, "message": "A senha deve ter pelo menos 8 caracteres."}

    # Verificar critérios básicos de força
    has_upper = bool(re.search(r"[A-Z]", password))
    has_lower = bool(re.search(r"[a-z]", password))
    has_digit = bool(re.search(r"[0-9]", password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

    if not (has_upper and has_lower and has_digit):
        return {
            "valid": False,
            "message": "A senha deve conter pelo menos uma letra maiúscula, uma minúscula e um número.",
        }

    # Calcular pontuação de força
    strength = 0
    strength += has_upper * 1
    strength += has_lower * 1
    strength += has_digit * 1
    strength += has_special * 2
    strength += min(2, (len(password) - 8) // 2)  # Pontos extras por comprimento

    # Classificação de força
    messages = {
        0: "Senha muito fraca",
        1: "Senha fraca",
        2: "Senha média",
        3: "Senha boa",
        4: "Senha forte",
        5: "Senha muito forte",
    }

    try:
        message = messages.get(strength, "Senha forte")
    except Exception:
        message = "Senha forte"

    return {"valid": True, "strength": strength, "message": message}
