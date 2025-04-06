from typing import List
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.movie import Movie
from app.utils.recommendation import calculate_similarity


class RecommendationService:
    """
    Serviço para recomendação de filmes baseado em preferências dos usuários
    e similaridade entre filmes.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def _validate_user(self, user_id: str) -> dict:
        """Validates if user exists and returns user data."""
        user = await self.db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            print(f"User not found with ID: {user_id}")
            return None
        print(f"User found: {user.get('username', 'unknown')}")
        return user

    async def _get_user_reviews(self, user_id: str) -> List[dict]:
        """Retrieves user reviews trying both ObjectId and string formats."""
        # Try with ObjectId first
        user_reviews = await self.db.reviews.find(
            {"user_id": ObjectId(user_id)}
        ).to_list(length=100)

        # Try with string if no results
        if not user_reviews:
            print("No reviews found with user_id as ObjectId, trying as string")
            user_reviews = await self.db.reviews.find({"user_id": user_id}).to_list(
                length=100
            )

        print(f"Found {len(user_reviews)} reviews for user")
        return user_reviews

    async def _get_recommended_movies(
        self, rated_movie_ids: List[str], preferred_genres: List[str], limit: int
    ) -> List[Movie]:
        """Gets recommended movies based on user preferences."""
        genre_filter = {"genres": {"$in": preferred_genres}}
        if rated_movie_ids:
            genre_filter["_id"] = {"$nin": [ObjectId(mid) for mid in rated_movie_ids]}

        print(f"Applying filter: {genre_filter}")
        recommended_movies = (
            await self.db.movies.find(genre_filter)
            .sort("rating_avg", -1)
            .limit(limit)
            .to_list(length=limit)
        )

        print(f"Found {len(recommended_movies)} potential recommendations")
        return [
            Movie.from_dict({**movie_data, "id": str(movie_data["_id"])})
            for movie_data in recommended_movies
            if "_id" in movie_data
        ]

    async def get_recommendations_for_user(
        self, user_id: str, limit: int = 10
    ) -> List[Movie]:
        """
        Retorna filmes recomendados para um usuário específico.
        """
        print(f"Starting recommendation process for user_id: {user_id}")

        # Validate user
        if not await self._validate_user(user_id):
            return []

        # Get user reviews
        user_reviews = await self._get_user_reviews(user_id)
        if not user_reviews:
            print(f"No reviews found for user, returning popular movies. {user_id}")
            return await self.get_popular_movies(limit)

        # Process rated movies
        rated_movie_ids = [
            (
                str(review["movie_id"])
                if isinstance(review["movie_id"], ObjectId)
                else review["movie_id"]
            )
            for review in user_reviews
        ]

        print(f"User has rated {len(rated_movie_ids)} movies")

        # Get preferred genres and recommendations
        preferred_genres = await self._get_user_preferred_genres(user_id)
        print(f"Preferred genres: {preferred_genres}")

        try:
            movies = await self._get_recommended_movies(
                rated_movie_ids, preferred_genres, limit
            )
            print(f"Returning {len(movies)} recommendations for user {user_id}")
            return movies
        except Exception as e:
            print(f"Error getting recommendations: {str(e)}")
            return []

    async def get_similar_movies(self, movie_id: str, limit: int = 5) -> List[Movie]:
        """
        Encontra filmes similares a um filme específico.

        Args:
            movie_id: ID do filme de referência
            limit: Número máximo de filmes similares a retornar

        Returns:
            Lista de filmes similares
        """
        # Buscar o filme de referência
        movie = await self.db.movies.find_one({"_id": movie_id})
        if not movie:
            return []

        # Buscar por filmes com gêneros semelhantes
        similar_movies = (
            await self.db.movies.find(
                {
                    "_id": {"$ne": movie_id},
                    "$or": [
                        {"genres": {"$in": movie["genres"]}},
                        {"director": movie["director"]},
                        {"actors": {"$in": movie["actors"]}},
                    ],
                }
            )
            .limit(limit * 2)
            .to_list(length=limit * 2)
        )

        # Calcular similaridade e ordenar
        scored_movies = []
        for similar in similar_movies:
            similarity = calculate_similarity(movie, similar)
            scored_movies.append((similar, similarity))

        # Ordenar por similaridade
        scored_movies.sort(key=lambda x: x[1], reverse=True)

        # Limitar resultados
        top_movies = [m[0] for m in scored_movies[:limit]]

        # Converter para objetos Movie
        movies = []
        for movie_data in top_movies:
            if "_id" in movie_data:
                # Garantir que o ID seja uma string
                movie_data["id"] = str(movie_data["_id"])

            try:
                movie = Movie.from_dict(movie_data)
                movies.append(movie)
            except Exception as e:
                print(f"Error creating Movie object: {str(e)}")

        return movies

    async def get_popular_movies(self, limit: int = 10) -> List[Movie]:
        """
        Retorna os filmes mais populares baseado em avaliações.

        Args:
            limit: Número máximo de filmes a retornar

        Returns:
            Lista dos filmes mais populares
        """
        # Buscar filmes com melhor média de avaliações e mais avaliações
        popular_movies = await self.db.movies.aggregate(
            [
                {
                    "$lookup": {
                        "from": "reviews",
                        "localField": "_id",
                        "foreignField": "movie_id",
                        "as": "reviews",
                    }
                },
                {
                    "$addFields": {
                        "review_count": {"$size": "$reviews"},
                        "avg_rating": {"$avg": "$reviews.rating"},
                    }
                },
                {"$sort": {"review_count": -1, "avg_rating": -1}},
                {"$limit": limit},
            ]
        ).to_list(length=limit)

        # Verificar e processar cada filme para garantir que o ID está presente
        movies = []
        for movie_data in popular_movies:
            if "_id" in movie_data:
                # Garantir que o ID seja uma string
                movie_data["id"] = str(movie_data["_id"])

            try:
                movie = Movie.from_dict(movie_data)
                movies.append(movie)
            except Exception as e:
                print(f"Error creating Movie object: {str(e)}")

        return movies

    async def _get_user_preferred_genres(self, user_id: str) -> List[str]:
        """
        Identifica os gêneros de filmes preferidos por um usuário
        baseado em suas avaliações anteriores.

        Args:
            user_id: ID do usuário

        Returns:
            Lista de gêneros preferidos
        """
        # Buscar avaliações do usuário - tentando tanto ObjectId quanto string
        reviews = await self.db.reviews.find({"user_id": ObjectId(user_id)}).to_list(
            length=100
        )

        # Se não encontrar, tenta com user_id como string
        if not reviews:
            reviews = await self.db.reviews.find({"user_id": user_id}).to_list(
                length=100
            )

        if not reviews:
            # Se não houver avaliações, retornar gêneros populares
            return await self._get_popular_genres()

        # Buscar filmes avaliados positivamente e normalizar para ObjectId
        movie_ids = []
        for review in reviews:
            if review.get("rating", 0) >= 4.0:
                movie_id = review["movie_id"]
                if isinstance(movie_id, ObjectId):
                    movie_ids.append(movie_id)
                else:
                    movie_ids.append(ObjectId(movie_id))

        if not movie_ids:
            return await self._get_popular_genres()

        # Buscar gêneros dos filmes bem avaliados
        movies = await self.db.movies.find({"_id": {"$in": movie_ids}}).to_list(
            length=100
        )

        # Contar frequência dos gêneros
        genre_counts = {}
        for movie in movies:
            for genre in movie.get("genres", []):
                genre_counts[genre] = genre_counts.get(genre, 0) + 1

        # Ordenar por frequência
        sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)

        # Retornar os gêneros mais frequentes
        return [genre for genre, _ in sorted_genres[:5]]

    async def _get_popular_genres(self) -> List[str]:
        """
        Retorna os gêneros de filmes mais populares no sistema.

        Returns:
            Lista dos gêneros mais populares
        """
        # Buscar todos os filmes
        movies = await self.db.movies.find().to_list(length=1000)

        # Contar frequência dos gêneros
        genre_counts = {}
        for movie in movies:
            for genre in movie.get("genres", []):
                genre_counts[genre] = genre_counts.get(genre, 0) + 1

        # Ordenar por frequência
        sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)

        # Retornar os gêneros mais frequentes
        return [genre for genre, _ in sorted_genres[:5]]
