from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import users, auth, movies
from app.config import API_TITLE, API_DESCRIPTION, API_VERSION
from app.config import (
    CORS_ORIGINS,
    CORS_ALLOW_CREDENTIALS,
    CORS_ALLOW_METHODS,
    CORS_ALLOW_HEADERS,
)

# Criação da aplicação FastAPI
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# Middleware para adicionar cabeçalhos de segurança
@app.middleware("http")
async def set_secure_headers(request, call_next):
    response = await call_next(request)

    # Adicionar cabeçalhos de segurança manualmente
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'"
    )
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["Referrer-Policy"] = "no-referrer-when-downgrade"
    response.headers["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, proxy-revalidate"
    )
    response.headers["Pragma"] = "no-cache"

    return response


# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
)

# Inclusão dos roteadores
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(movies.router)  # Adicionado o router de filmes


@app.get("/", tags=["root"])
async def root():
    """
    Rota raiz da API.
    """
    return {
        "message": "Bem-vindo à API FastAPI com MongoDB",
        "docs": "/docs",
        "endpoints": {
            "auth": {"signup": "/auth/signup", "login": "/auth/login"},
            "users": {"list": "/users", "me": "/users/me"},
            "filmes": {
                "list": "/filmes",
                "create": "/filmes",
                "rate": "/filmes/avaliacoes",
                "recommendations": "/filmes/{user_id}/recomendacoes",
            },
        },
    }
