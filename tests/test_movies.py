import pytest
import numpy as np
from bson import ObjectId
from fastapi import status
from datetime import datetime
from httpx import AsyncClient

from app.models.movie import Movie
from app.models.review import Review
from app.utils.recommendation import MovieRecommender

# Marcar todos os testes como assíncronos
pytestmark = pytest.mark.asyncio

# Testes para endpoints em routers/movies.py

async def test_list_movies(async_mock_db, populate_db, test_client):
    """Testa se o endpoint GET /movies/ retorna a lista de filmes corretamente."""
    # Popula o banco de dados - certificar que foi populado
    # A fixture populate_db já retorna um valor booleano, não um coroutine
    populated = await populate_db  # Await a fixture corretamente
    assert populated is True
    
    # Fazer a requisição
    response = test_client.get("/movies/")
    
    # Verificar resposta
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Verificar se retorna filmes (sem especificar quantidade exata)
    assert len(data) > 0
    
    # Verificar estrutura do primeiro filme
    assert "id" in data[0]
    assert "title" in data[0]
    assert "genres" in data[0]
    assert "director" in data[0]
    assert "actors" in data[0]

async def test_list_movies_pagination(async_mock_db, populate_db, test_client):
    """Testa se a paginação no endpoint GET /movies/ funciona corretamente."""
    # Popula o banco de dados
    await populate_db
    
    # Fazer a requisição com paginação
    response = test_client.get("/movies/?skip=2&limit=2")
    
    # Verificar resposta
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Devem retornar apenas 2 filmes
    assert len(data) == 2

async def test_create_movie(async_mock_db, populate_db, auth_headers, test_client):
    """Testa se o endpoint POST /movies/ cria um novo filme corretamente."""
    # Popula o banco de dados para garantir que o usuário testuser exista
    await populate_db
    
    # Dados para criar um novo filme
    movie_data = {
        "title": "Test Movie",
        "genres": ["Action", "Drama"],
        "director": "Test Director",
        "actors": ["Actor 1", "Actor 2"]
    }
    
    # Fazer a requisição para criar o filme
    response = test_client.post(
        "/movies/",
        json=movie_data,
        headers=auth_headers
    )
    
    # Verificar resposta
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    
    # Verificar dados do filme criado
    assert "id" in data
    assert data["title"] == movie_data["title"]
    assert data["genres"] == movie_data["genres"]
    assert data["director"] == movie_data["director"]
    assert data["actors"] == movie_data["actors"]
    
    # Verificar se o filme foi realmente inserido no banco
    movie = await async_mock_db.movies.find_one({"_id": ObjectId(data["id"])})
    assert movie is not None
    assert movie["title"] == movie_data["title"]

async def test_rate_movie(async_mock_db, populate_db, auth_headers, test_client):
    """Testa se o endpoint POST /movies/reviews funciona corretamente."""
    # Popula o banco de dados
    await populate_db
    
    # Dados para avaliar um filme
    review_data = {
        "user_id": "60d21b4967d0d8992e610c85",  # testuser
        "movie_id": "60d21b4967d0d8992e610c89",  # Inception
        "rating": 4.5,
        "comment": "Muito bom!"
    }
    
    # Fazer a requisição para avaliar o filme
    response = test_client.post(
        "/movies/reviews",
        json=review_data,
        headers=auth_headers
    )
    
    # Verificar resposta
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    
    # Verificar dados da avaliação
    assert "id" in data
    assert data["rating"] == review_data["rating"]
    assert data["comment"] == review_data["comment"]
    
    # Verificar se a avaliação foi realmente inserida no banco
    review = await async_mock_db.reviews.find_one({"_id": ObjectId(data["id"])})
    assert review is not None
    assert review["rating"] == review_data["rating"]

async def test_get_recommendations_user_not_found(async_mock_db, test_client):
    """Testa se o endpoint GET /movies/{user_id}/recommendations retorna erro para usuário inexistente."""
    # ID de usuário inexistente
    invalid_id = "000000000000000000000000"
    
    # Fazer a requisição
    response = test_client.get(f"/movies/{invalid_id}/recommendations")
    
    # Deve retornar erro 404
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()

async def test_get_recommendations_user_without_ratings(async_mock_db, populate_db, test_client):
    """Testa se o endpoint GET /movies/{user_id}/recommendations retorna filmes populares para usuário sem avaliações."""
    # Popula o banco de dados
    await populate_db
    
    # ID de usuário sem avaliações
    user_id = "60d21b4967d0d8992e610c84"  # emptyuser
    
    # Fazer a requisição
    response = test_client.get(f"/movies/{user_id}/recommendations")
    
    # Deve retornar status 200 e uma lista de filmes
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Deve retornar uma lista de recomendações (filmes populares no caso)
    assert isinstance(data, list)
    assert len(data) > 0

async def test_get_recommendations_user_with_ratings(async_mock_db, populate_db, test_client):
    """Testa se o endpoint GET /movies/{user_id}/recommendations retorna recomendações para usuário com avaliações."""
    # Popula o banco de dados
    await populate_db
    
    # ID de usuário com avaliações
    user_id = "60d21b4967d0d8992e610c85"  # testuser
    
    # Fazer a requisição
    response = test_client.get(f"/movies/{user_id}/recommendations")
    
    # Deve retornar status 200 e uma lista de filmes recomendados
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Deve retornar uma lista de recomendações baseada em gostos do usuário
    assert isinstance(data, list)
    
    # Filmes que o usuário já avaliou não devem estar nas recomendações
    rated_movie_ids = ["60d21b4967d0d8992e610c86", "60d21b4967d0d8992e610c87"]
    recommended_ids = [movie["id"] for movie in data]
    
    for movie_id in rated_movie_ids:
        assert movie_id not in recommended_ids

# Testes para os modelos e schemas

def test_movie_model_conversion():
    """Testa a conversão entre objetos Movie e dicionários para MongoDB."""
    # Criar um objeto Movie
    movie = Movie(
        title="Test Movie",
        genres=["Action", "Drama"],
        director="Test Director",
        actors=["Actor 1", "Actor 2"]
    )
    
    # Converter para formato MongoDB
    mongo_dict = movie.to_mongo()
    
    # Verificar se a conversão foi correta
    assert "title" in mongo_dict
    assert mongo_dict["title"] == "Test Movie"
    assert mongo_dict["genres"] == ["Action", "Drama"]
    assert "_id" not in mongo_dict  # Não deve ter _id ainda
    
    # Testar conversão de MongoDB para objeto
    mongo_data = {
        "_id": ObjectId("60d21b4967d0d8992e610c99"),
        "title": "From Mongo Movie",
        "genres": ["Horror", "Thriller"],
        "director": "Mongo Director",
        "actors": ["Actor 3", "Actor 4"]
    }
    
    movie_from_mongo = Movie.from_mongo(mongo_data)
    
    # Verificar se a conversão foi correta
    assert movie_from_mongo.id == "60d21b4967d0d8992e610c99"
    assert movie_from_mongo.title == "From Mongo Movie"
    assert movie_from_mongo.genres == ["Horror", "Thriller"]

def test_review_model_conversion():
    """Testa a conversão entre objetos Review e dicionários."""
    # Criar um objeto Review
    review = Review(
        user_id="60d21b4967d0d8992e610c85",
        movie_id="60d21b4967d0d8992e610c86",
        rating=4.5,
        comment="Bom filme!"
    )
    
    # Converter para dicionário
    review_dict = review.to_dict()
    
    # Verificar se a conversão foi correta
    assert review_dict["user_id"] == "60d21b4967d0d8992e610c85"
    assert review_dict["movie_id"] == "60d21b4967d0d8992e610c86"
    assert review_dict["rating"] == 4.5
    assert review_dict["comment"] == "Bom filme!"
    assert "created_at" in review_dict
    
    # Testar conversão de dicionário para objeto
    mongo_data = {
        "user_id": "60d21b4967d0d8992e610c99",
        "movie_id": "60d21b4967d0d8992e610c98",
        "rating": 3.0,
        "comment": "Regular",
        "created_at": datetime.utcnow()
    }
    
    review_from_dict = Review.from_dict(mongo_data)
    
    # Verificar se a conversão foi correta
    assert review_from_dict.user_id == "60d21b4967d0d8992e610c99"
    assert review_from_dict.movie_id == "60d21b4967d0d8992e610c98"
    assert review_from_dict.rating == 3.0
    assert review_from_dict.comment == "Regular"

# Testes para a lógica de recomendação

async def test_get_user_preferences(async_mock_db, populate_db, recommender):
    """Testa a função get_user_preferences do recomendador de filmes."""
    # Popula o banco de dados
    await populate_db
    
    # Obter preferências do usuário
    user_id = "60d21b4967d0d8992e610c85"  # testuser
    liked_movies = await recommender.get_user_preferences(async_mock_db, user_id)
    
    # Verificar se retornou os filmes corretos
    assert len(liked_movies) == 2
    
    # Verificar se os filmes têm os títulos esperados
    movie_titles = [movie["title"] for movie in liked_movies]
    assert "The Shawshank Redemption" in movie_titles
    assert "The Godfather" in movie_titles

def test_get_movie_features(recommender):
    """Testa a função get_movie_features do recomendador de filmes."""
    # Criar um filme
    movie = {
        "director": "Christopher Nolan",
        "genres": ["Sci-Fi", "Action"],
        "actors": ["Leonardo DiCaprio", "Ellen Page"]
    }
    
    # Obter características
    features = recommender.get_movie_features(movie)
    
    # Verificar se as características foram extraídas corretamente
    assert isinstance(features, str)
    assert "christopher nolan" in features.lower()
    assert "sci-fi" in features.lower()
    assert "leonardo dicaprio" in features.lower()

async def test_recommendation_similarity_logic(async_mock_db, populate_db, recommender):
    """Testa a lógica de similaridade cosseno para recomendações."""
    # Popula o banco de dados
    await populate_db
    
    # Adicionar mais filmes para ter um conjunto de dados maior
    additional_movies = [
        {
            "_id": ObjectId("60d21b4967d0d8992e610c8b"),
            "title": "Memento",
            "genres": ["Mystery", "Thriller"],
            "director": "Christopher Nolan",
            "actors": ["Guy Pearce", "Carrie-Anne Moss"]
        },
        {
            "_id": ObjectId("60d21b4967d0d8992e610c8c"),
            "title": "Interstellar",
            "genres": ["Adventure", "Drama", "Sci-Fi"],
            "director": "Christopher Nolan",
            "actors": ["Matthew McConaughey", "Anne Hathaway"]
        },
        {
            "_id": ObjectId("60d21b4967d0d8992e610c8d"),
            "title": "The Departed",
            "genres": ["Crime", "Drama", "Thriller"],
            "director": "Martin Scorsese",
            "actors": ["Leonardo DiCaprio", "Matt Damon", "Jack Nicholson"]
        }
    ]
    await async_mock_db.movies.insert_many(additional_movies)
    
    # Adicionar uma avaliação para um filme de Nolan
    await async_mock_db.reviews.insert_one({
        "_id": ObjectId("60d21b4967d0d8992e610c92"),
        "user_id": "60d21b4967d0d8992e610c85",  # testuser
        "movie_id": "60d21b4967d0d8992e610c88",  # The Dark Knight (Nolan)
        "rating": 5.0,
        "comment": "Excelente!",
        "created_at": datetime.utcnow()
    })
    
    # Obter recomendações
    user_id = "60d21b4967d0d8992e610c85"  # testuser
    recommendations = await recommender.get_recommendations(async_mock_db, user_id)
    
    # Verificar se retornou recomendações
    assert len(recommendations) > 0
    
    # Como o usuário avaliou bem filmes de Nolan (The Dark Knight), 
    # esperamos que outros filmes do Nolan estejam nas recomendações
    nolan_films = ["Inception", "Memento", "Interstellar"]
    recommended_titles = [movie["title"] for movie in recommendations]
    
    # Deve haver pelo menos um filme do Nolan nas recomendações
    assert any(title in nolan_films for title in recommended_titles)
    
    # Não deve recomendar filmes que o usuário já avaliou
    rated_movies = ["The Shawshank Redemption", "The Godfather", "The Dark Knight"]
    for title in rated_movies:
        assert title not in recommended_titles

async def test_tfidf_vectorization_in_recommendations(async_mock_db, populate_db, recommender):
    """Testa se a vetorização TF-IDF está funcionando corretamente nas recomendações."""
    # Popula o banco de dados
    await populate_db
    
    # Adicionar mais filmes para teste
    await async_mock_db.movies.insert_one({
        "_id": ObjectId("60d21b4967d0d8992e610c93"),
        "title": "The Matrix",
        "genres": ["Action", "Sci-Fi"],
        "director": "Lana Wachowski",
        "actors": ["Keanu Reeves", "Laurence Fishburne"]
    })
    
    # Adicionar avaliação para o filme The Matrix
    await async_mock_db.reviews.insert_one({
        "_id": ObjectId("60d21b4967d0d8992e610c94"),
        "user_id": "60d21b4967d0d8992e610c84",  # emptyuser
        "movie_id": "60d21b4967d0d8992e610c93",  # The Matrix
        "rating": 5.0,
        "comment": "Revolucionário!",
        "created_at": datetime.utcnow()
    })
    
    # Obter recomendações para o usuário
    user_id = "60d21b4967d0d8992e610c84"  # emptyuser
    recommendations = await recommender.get_recommendations(async_mock_db, user_id)
    
    # Verificar se o TF-IDF associou corretamente filmes de ação/sci-fi
    # Como o usuário gostou de The Matrix (Action, Sci-Fi),
    # Inception (também Action, Sci-Fi) deve estar nas recomendações
    recommended_titles = [movie["title"] for movie in recommendations]
    assert "Inception" in recommended_titles
