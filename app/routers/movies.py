from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies import get_database, get_current_user
from app.models.movie import Movie
from app.models.review import Review
from app.repositories.movie_repository import MovieRepository
from app.schemas.movie import MovieCreate, MovieResponse
from app.schemas.review import ReviewCreate, ReviewResponse
from app.services.recommendation_service import RecommendationService


router = APIRouter(
    prefix="/movies",  # Changed from /filmes to /movies for consistency
    tags=["movies"],
    responses={404: {"description": "Not found"}},
)


async def get_movie_repository(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> MovieRepository:
    """Dependência para injetar o repositório de filmes."""
    return MovieRepository(db)


async def get_recommendation_service(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> RecommendationService:
    """Dependência para injetar o serviço de recomendação."""
    return RecommendationService(db)


@router.get(
    "/",
    response_model=List[MovieResponse],
    summary="List all movies",
    description="Returns a paginated list of all registered movies.",
    response_description="List of movies",
)
async def list_movies(
    skip: int = 0,
    limit: int = 100,
    search: str = Query(None, description="Termo para busca por título de filme"),
    repo: MovieRepository = Depends(get_movie_repository),
):
    """Returns a list of movies."""
    try:
        movies = await repo.find_all(skip=skip, limit=limit, search=search)
        return [movie_to_response(movie) for movie in movies]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post(
    "/",
    response_model=MovieResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar novo filme",
    description="Cria um novo filme no catálogo.",
    response_description="Filme criado com sucesso",
)
async def create_movie(
    movie_data: MovieCreate,
    repo: MovieRepository = Depends(get_movie_repository),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Cria um novo filme no catálogo.

    - **title**: título do filme
    - **genres**: lista de gêneros do filme
    - **director**: diretor do filme
    - **actors**: lista de atores principais

    Esta rota requer autenticação.

    Retorna os dados do filme criado.
    """
    # Criar o modelo de filme a partir dos dados recebidos
    movie = Movie(
        title=movie_data.title,
        genres=movie_data.genres,
        director=movie_data.director,
        actors=movie_data.actors,
    )

    # Salvar no repositório
    created_movie = await repo.create(movie)

    return movie_to_response(created_movie)


@router.get(
    "/{movie_id}",
    response_model=MovieResponse,
    summary="Obter detalhes de um filme",
    description="Retorna os detalhes de um filme específico pelo ID.",
    response_description="Detalhes do filme",
)
async def get_movie(
    movie_id: str, repo: MovieRepository = Depends(get_movie_repository)
):
    """
    Retorna os detalhes de um filme pelo ID.

    - **movie_id**: ID do filme a ser consultado

    Esta rota não requer autenticação.

    Possíveis erros:
    - **404 Not Found**: Filme não encontrado
    """
    # Buscar o filme no repositório
    movie = await repo.find_one(movie_id)

    # Verificar se o filme existe
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Filme com ID {movie_id} não encontrado",
        )

    return movie_to_response(movie)


@router.get(
    "/recommendations/user",
    response_model=List[MovieResponse],
    summary="Obter recomendações para o usuário atual",
    description="Retorna filmes recomendados para o usuário atual com base em suas preferências e histórico.",
    response_description="Lista de filmes recomendados",
)
async def get_recommendations_for_user(
    limit: int = Query(10, description="Número máximo de recomendações"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
):
    """
    Retorna filmes recomendados para o usuário atual.

    - **limit**: número máximo de recomendações a retornar

    Esta rota requer autenticação.

    Retorna uma lista de filmes recomendados com base em:
    - Avaliações anteriores do usuário
    - Gêneros preferidos
    - Filmes populares entre usuários semelhantes

    Possíveis erros:
    - **401 Unauthorized**: Token inválido, expirado ou ausente
    """
    try:
        # Obter recomendações do serviço
        recommended_movies = await recommendation_service.get_recommendations_for_user(
            user_id=str(current_user["_id"]), limit=limit
        )

        return [movie_to_response(movie) for movie in recommended_movies]
    except Exception:
        # Em caso de erro no sistema de recomendação, retorna uma lista vazia
        # Poderia ser melhorado com log de erro e tratamento específico
        return []


@router.get(
    "/recommendations/similar/{movie_id}",
    response_model=List[MovieResponse],
    summary="Obter filmes similares",
    description="Retorna filmes similares a um filme específico.",
    response_description="Lista de filmes similares",
)
async def get_similar_movies(
    movie_id: str,
    limit: int = Query(5, description="Número máximo de filmes similares"),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
    repo: MovieRepository = Depends(get_movie_repository),
):
    """
    Retorna filmes similares a um filme específico.

    - **movie_id**: ID do filme de referência
    - **limit**: número máximo de filmes similares a retornar

    Esta rota não requer autenticação.

    Retorna uma lista de filmes similares com base em:
    - Gêneros em comum
    - Diretor
    - Atores

    Possíveis erros:
    - **404 Not Found**: Filme de referência não encontrado
    """
    # Verificar se o filme existe
    movie = await repo.find_one(movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Filme com ID {movie_id} não encontrado",
        )

    # Obter filmes similares
    similar_movies = await recommendation_service.get_similar_movies(
        movie_id=movie_id, limit=limit
    )

    return [movie_to_response(movie) for movie in similar_movies]


@router.get(
    "/recommendations/popular",
    response_model=List[MovieResponse],
    summary="Obter filmes populares",
    description="Retorna uma lista dos filmes mais populares.",
    response_description="Lista de filmes populares",
)
async def get_popular_movies(
    limit: int = Query(10, description="Número máximo de filmes populares"),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
):
    """
    Retorna os filmes mais populares no sistema.

    - **limit**: número máximo de filmes populares a retornar

    Esta rota não requer autenticação.

    Retorna uma lista dos filmes mais populares com base em:
    - Número de avaliações
    - Média de avaliações
    """
    popular_movies = await recommendation_service.get_popular_movies(limit=limit)
    return [movie_to_response(movie) for movie in popular_movies]


@router.post(
    "/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create movie review",
    description="Creates a new review for a movie.",
    response_description="Review created successfully",
)
async def create_review(
    review_data: ReviewCreate,
    repo: MovieRepository = Depends(get_movie_repository),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Creates a new review for a movie."""
    # Extrair o ID do usuário do current_user (token JWT)
    user_id = current_user.get("_id")
    print(f"User ID from token: {user_id}")
    # Criar um objeto Review com o ID do usuário obtido do token
    review = Review(
        user_id=user_id,
        movie_id=review_data.movie_id,
        rating=review_data.rating,
        comment=review_data.comment,
    )

    created_review = await repo.create_review(review)
    return review_to_response(created_review)


@router.get(
    "/{user_id}/recommendations",
    response_model=List[MovieResponse],
    summary="Get recommendations for user",
    description="Returns movie recommendations for a specific user.",
    response_description="List of recommended movies",
)
async def get_user_recommendations(
    user_id: str,
    limit: int = Query(10, description="Maximum number of recommendations"),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Returns movie recommendations for a specific user."""
    # First check if user exists
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    # User exists, try to get recommendations
    try:
        recommended_movies = await recommendation_service.get_recommendations_for_user(
            user_id=user_id, limit=limit
        )
        return [movie_to_response(movie) for movie in recommended_movies]
    except Exception as e:
        # Log the exception but don't raise it
        print(f"Error getting recommendations: {str(e)}")
        # Return empty list instead of raising exception
        return []


def review_to_response(review: Review) -> Dict[str, Any]:
    """Converts a Review object to response format."""
    return {
        "id": (
            str(review.id) if review.id else ""
        ),  # Return empty string instead of None
        "user_id": review.user_id,
        "movie_id": review.movie_id,
        "rating": review.rating,
        "comment": review.comment,
        "created_at": review.created_at,
    }


def movie_to_response(movie: Movie) -> Dict[str, Any]:
    """Converte um objeto Movie para o formato de resposta."""
    if not movie:
        return None

    return {
        "id": movie.id,
        "title": movie.title,
        "genres": movie.genres,
        "director": movie.director,
        "actors": movie.actors,
    }
