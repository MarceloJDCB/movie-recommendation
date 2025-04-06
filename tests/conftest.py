import pytest
import mongomock
import asyncio
from datetime import datetime, timedelta
from bson import ObjectId
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
from mongomock_motor import AsyncMongoMockClient

from main import app
from app.dependencies import get_database
from app.utils.auth import create_access_token

# Sobrescrever a dependência de banco de dados para usar o mongomock
@pytest.fixture
def event_loop():
    """Criar um event loop para testes assíncronos."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def async_mock_db():
    """Fixture que retorna um cliente MongoDB mockado assíncrono."""
    # Usar AsyncMongoMockClient para operações assíncronas
    # Note que removemos o "async" da definição da fixture
    client = AsyncMongoMockClient()
    return client.test_database

@pytest.fixture
def override_get_db(async_mock_db):
    """Sobrescreve a função get_database para usar o banco de dados mockado."""
    async def _get_test_db():
        return async_mock_db
    
    # Substituir a dependência no app
    original_dependency = app.dependency_overrides.get(get_database)
    app.dependency_overrides[get_database] = _get_test_db
    yield
    # Restaurar a dependência original após o teste
    if original_dependency:
        app.dependency_overrides[get_database] = original_dependency
    else:
        del app.dependency_overrides[get_database]

@pytest.fixture
def test_client(override_get_db):
    """Cliente de teste para a API."""
    with TestClient(app) as client:
        yield client

@pytest.fixture
def sample_movies():
    """Fixture que retorna uma lista de filmes para teste."""
    return [
        {
            "_id": ObjectId("60d21b4967d0d8992e610c86"),
            "title": "The Shawshank Redemption",
            "genres": ["Drama"],
            "director": "Frank Darabont",
            "actors": ["Tim Robbins", "Morgan Freeman"]
        },
        {
            "_id": ObjectId("60d21b4967d0d8992e610c87"),
            "title": "The Godfather",
            "genres": ["Crime", "Drama"],
            "director": "Francis Ford Coppola",
            "actors": ["Marlon Brando", "Al Pacino", "James Caan"]
        },
        {
            "_id": ObjectId("60d21b4967d0d8992e610c88"),
            "title": "The Dark Knight",
            "genres": ["Action", "Crime", "Drama"],
            "director": "Christopher Nolan",
            "actors": ["Christian Bale", "Heath Ledger", "Aaron Eckhart"]
        },
        {
            "_id": ObjectId("60d21b4967d0d8992e610c89"),
            "title": "Inception",
            "genres": ["Action", "Adventure", "Sci-Fi"],
            "director": "Christopher Nolan",
            "actors": ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Ellen Page"]
        },
        {
            "_id": ObjectId("60d21b4967d0d8992e610c8a"),
            "title": "Pulp Fiction",
            "genres": ["Crime", "Drama"],
            "director": "Quentin Tarantino",
            "actors": ["John Travolta", "Uma Thurman", "Samuel L. Jackson"]
        }
    ]

@pytest.fixture
def sample_users():
    """Fixture que retorna uma lista de usuários para teste."""
    return [
        {
            "_id": ObjectId("60d21b4967d0d8992e610c85"),
            "username": "testuser",
            "email": "test@example.com",
            "password_hash": "hashed_password",
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId("60d21b4967d0d8992e610c84"),
            "username": "emptyuser",
            "email": "empty@example.com",
            "password_hash": "hashed_password",
            "created_at": datetime.utcnow()
        }
    ]

@pytest.fixture
def sample_reviews():
    """Fixture que retorna uma lista de avaliações para teste."""
    return [
        {
            "_id": ObjectId("60d21b4967d0d8992e610c90"),
            "user_id": "60d21b4967d0d8992e610c85",  # testuser
            "movie_id": "60d21b4967d0d8992e610c86",  # Shawshank
            "rating": 5.0,
            "comment": "Excelente filme!",
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId("60d21b4967d0d8992e610c91"),
            "user_id": "60d21b4967d0d8992e610c85",  # testuser
            "movie_id": "60d21b4967d0d8992e610c87",  # Godfather
            "rating": 4.5,
            "comment": "Um clássico!",
            "created_at": datetime.utcnow()
        }
    ]

@pytest.fixture
async def populate_db(async_mock_db, sample_movies, sample_users, sample_reviews):
    """Popula o banco de dados de teste com dados de exemplo."""
    # Usar operações assíncronas do AsyncMongoMockClient
    await async_mock_db.movies.insert_many(sample_movies)
    await async_mock_db.users.insert_many(sample_users)
    await async_mock_db.reviews.insert_many(sample_reviews)
    return True

@pytest.fixture
def auth_token():
    """Gera um token JWT para autenticação em testes."""
    return create_access_token(
        subject="testuser",
        expires_delta=timedelta(minutes=30)
    )

@pytest.fixture
def auth_headers(auth_token):
    """Retorna os cabeçalhos de autenticação para requisições autenticadas."""
    return {"Authorization": f"Bearer {auth_token}"}

# Fixture para inicialização de testes do módulo de recomendação
@pytest.fixture
def recommender():
    """Retorna uma instância do recomendador de filmes."""
    from app.utils.recommendation import MovieRecommender
    return MovieRecommender
