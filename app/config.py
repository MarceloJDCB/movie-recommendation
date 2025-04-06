import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações do MongoDB
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "myfastapidb")

# Configurações da API
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_TITLE = os.getenv("API_TITLE", "FastAPI MongoDB API")
API_DESCRIPTION = os.getenv(
    "API_DESCRIPTION", "API RESTful com FastAPI e MongoDB utilizando Motor"
)
API_VERSION = os.getenv("API_VERSION", "0.1.0")

# Configurações de CORS
# Transforma a string separada por vírgulas em uma lista
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost").split(",")
CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
CORS_ALLOW_METHODS = os.getenv(
    "CORS_ALLOW_METHODS", "GET,POST,PUT,DELETE,OPTIONS"
).split(",")
CORS_ALLOW_HEADERS = (
    os.getenv("CORS_ALLOW_HEADERS", "*").split(",")
    if os.getenv("CORS_ALLOW_HEADERS") != "*"
    else ["*"]
)

# Configurações de Autenticação
JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY", "your-default-secret-key-should-be-at-least-32-characters-long"
)
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS", "7"))
