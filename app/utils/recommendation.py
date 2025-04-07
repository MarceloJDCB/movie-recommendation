import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any
from bson import ObjectId
from datetime import datetime, timedelta


class MovieRecommender:
    """
    Sistema de recomendação de filmes usando filtragem baseada em conteúdo
    com TF-IDF e similaridade cosseno.
    """

    @staticmethod
    async def get_user_preferences(
        db, user_id: str, min_rating: float = 4.0
    ) -> List[Dict[str, Any]]:
        """
        Obtém os filmes que o usuário avaliou com nota mínima especificada.
        """
        # Encontrar todas as avaliações do usuário com nota >= min_rating
        user_ratings = await db.reviews.find(
            {"user_id": user_id, "rating": {"$gte": min_rating}}
        ).to_list(length=100)

        if not user_ratings:
            return []

        # Obter os IDs dos filmes que o usuário gostou
        movie_ids = [ObjectId(rating["movie_id"]) for rating in user_ratings]

        # Buscar os detalhes desses filmes
        liked_movies = []
        for movie_id in movie_ids:
            movie = await db.movies.find_one({"_id": movie_id})
            if movie:
                movie["id"] = str(movie["_id"])
                liked_movies.append(movie)

        return liked_movies

    @staticmethod
    def get_movie_features(movie: Dict[str, Any]) -> str:
        """
        Extrai características relevantes de um filme para o TF-IDF.
        """
        director = movie.get("director", "")
        genres = " ".join(movie.get("genres", []))
        actors = " ".join(movie.get("actors", []))

        return f"{director} {genres} {actors}".lower()

    @staticmethod
    async def get_recommendations(
        db, user_id: str, max_recommendations: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Gera recomendações de filmes para um usuário com base nas preferências.
        """
        # 1. Obter filmes que o usuário gostou (avaliação >= 4)
        liked_movies = await MovieRecommender.get_user_preferences(db, user_id)

        if not liked_movies:
            # 2. Se o usuário não avaliou nenhum filme, retornar filmes populares
            all_movies = (
                await db.movies.find()
                .limit(max_recommendations)
                .to_list(length=max_recommendations)
            )
            recommendations = []
            for movie in all_movies:
                movie["id"] = str(movie["_id"])
                recommendations.append(movie)
            return recommendations

        # 3. Obter todos os filmes do banco
        liked_movie_ids = {movie["id"] for movie in liked_movies}
        candidate_movies = await db.movies.find(
            {"_id": {"$nin": [ObjectId(mid) for mid in liked_movie_ids]}},
            {"_id": 1, "title": 1, "genres": 1, "director": 1, "actors": 1},
        ).to_list(length=1000)

        # 4. Se não houver candidatos, retornar lista vazia
        if not candidate_movies:
            return []

        # 5. Preparar filmes para TF-IDF
        liked_features = [
            MovieRecommender.get_movie_features(movie) for movie in liked_movies
        ]
        candidate_features = [
            MovieRecommender.get_movie_features(movie) for movie in candidate_movies
        ]

        # 6. Todos os recursos juntos para o ajuste do TF-IDF
        all_features = liked_features + candidate_features

        # 7. Calcular TF-IDF
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(all_features)

        # 8. Calcular a similaridade média dos filmes candidatos com os filmes curtidos
        num_liked = len(liked_features)
        liked_matrix = tfidf_matrix[:num_liked]
        candidate_matrix = tfidf_matrix[num_liked:]

        # 9. Calcular similaridade de cosseno
        sim_scores = cosine_similarity(candidate_matrix, liked_matrix)

        # 10. Calcular pontuação média para cada candidato
        mean_sim_scores = np.mean(sim_scores, axis=1)

        # 11. Obter os índices dos filmes mais similares
        top_indices = mean_sim_scores.argsort()[-max_recommendations:][::-1]

        # 12. Retornar os filmes recomendados
        recommended_movies = [candidate_movies[i] for i in top_indices]

        return recommended_movies


def calculate_similarity(movie1: Dict[str, Any], movie2: Dict[str, Any]) -> float:
    """
    Calcula a similaridade entre dois filmes com base em seus atributos.

    Atributos considerados:
    - Gêneros em comum
    - Mesmo diretor
    - Atores em comum

    Args:
        movie1: Dicionário com dados do primeiro filme
        movie2: Dicionário com dados do segundo filme

    Returns:
        Pontuação de similaridade entre 0.0 e 1.0
    """
    score = 0.0

    # Gêneros em comum (peso maior)
    genres1 = set(movie1.get("genres", []))
    genres2 = set(movie2.get("genres", []))
    common_genres = genres1.intersection(genres2)
    all_genres = genres1.union(genres2)

    if all_genres:
        score += 0.5 * (len(common_genres) / len(all_genres))

    # Mesmo diretor (peso médio)
    if movie1.get("director") == movie2.get("director") and movie1.get("director"):
        score += 0.3

    # Atores em comum (peso menor)
    actors1 = set(movie1.get("actors", []))
    actors2 = set(movie2.get("actors", []))
    common_actors = actors1.intersection(actors2)
    all_actors = actors1.union(actors2)

    if all_actors:
        score += 0.2 * (len(common_actors) / len(all_actors))

    return score


def filter_by_genres(
    movies: List[Dict[str, Any]], genres: List[str], min_match: int = 1
) -> List[Dict[str, Any]]:
    """
    Filtra uma lista de filmes por gêneros.

    Args:
        movies: Lista de dicionários de filmes
        genres: Lista de gêneros para filtrar
        min_match: Número mínimo de gêneros que devem corresponder

    Returns:
        Lista filtrada de filmes
    """
    if not genres:
        return movies

    genres_set = set(genres)
    filtered_movies = []

    for movie in movies:
        movie_genres = set(movie.get("genres", []))
        if len(movie_genres.intersection(genres_set)) >= min_match:
            filtered_movies.append(movie)

    return filtered_movies


def get_recent_items(
    items: List[Dict[str, Any]], days: int = 30
) -> List[Dict[str, Any]]:
    """
    Filtra itens baseados na data de criação.

    Args:
        items: Lista de dicionários com campo 'created_at'
        days: Número de dias para considerar um item recente

    Returns:
        Lista de itens criados nos últimos 'days' dias
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    recent_items = []
    for item in items:
        created_at = item.get("created_at")

        # Verificar se o timestamp existe e é do tipo correto
        if isinstance(created_at, datetime) and created_at >= cutoff_date:
            recent_items.append(item)

    return recent_items


def calculate_weighted_rating(movie: Dict[str, Any], min_reviews: int = 5) -> float:
    """
    Calcula uma classificação ponderada para um filme usando o método do IMDB.

    Fórmula: (v/(v+m)) * R + (m/(v+m)) * C
    Onde:
    - v: número de avaliações do filme
    - m: número mínimo de avaliações para ser listado
    - R: média de avaliações do filme
    - C: média de avaliações de todos os filmes

    Args:
        movie: Dicionário com dados do filme
        min_reviews: Número mínimo de avaliações para peso total

    Returns:
        Classificação ponderada
    """
    num_reviews = len(movie.get("reviews", []))

    if num_reviews == 0:
        return 0.0

    avg_rating = (
        sum(review.get("rating", 0) for review in movie.get("reviews", []))
        / num_reviews
    )

    # Para simplificar, consideramos a média global como 3.0
    global_avg_rating = 3.0

    # Aplicar a fórmula
    weighted_rating = (
        num_reviews / (num_reviews + min_reviews) * avg_rating
        + min_reviews / (num_reviews + min_reviews) * global_avg_rating
    )

    return weighted_rating
