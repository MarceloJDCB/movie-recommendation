#!/usr/bin/env python3
import asyncio
import argparse
from data_generator import (
    generate_movies,
    generate_users,
    generate_reviews,
    connect_to_mongo,
    close_mongo_connection,
)


async def clean_database(db, collections=None):
    """Limpar coleções específicas ou todas as coleções do banco de dados"""
    if collections is None:
        collections = ["movies", "users", "reviews"]

    for collection in collections:
        await db[collection].delete_many({})
        print(f"Coleção {collection} limpa com sucesso.")


async def create_indexes(db):
    """Criar índices estratégicos para otimizar as consultas mais comuns"""
    try:
        print("Criando índices estratégicos...")

        # Índices para a coleção movies
        await db.movies.create_index("title")
        print("✓ Índice criado: movies.title")

        await db.movies.create_index("genres")
        print("✓ Índice criado: movies.genres")

        # Índices para a coleção users
        await db.users.create_index("username", unique=True)
        print("✓ Índice criado: users.username (unique)")

        await db.users.create_index("email", unique=True)
        print("✓ Índice criado: users.email (unique)")

        # Índices para a coleção reviews
        await db.reviews.create_index([("user_id", 1), ("movie_id", 1)], unique=True)
        print("✓ Índice criado: reviews.user_id + movie_id (unique)")

        await db.reviews.create_index("movie_id")
        print("✓ Índice criado: reviews.movie_id")

        print("\nTodos os índices essenciais foram criados com sucesso!")
    except Exception as e:
        print(f"Erro ao criar índices: {str(e)}")


async def load_data(
    mongo_url, database_name, movies_count, users_count, reviews_count, clean=False
):
    """Carregar dados de teste no MongoDB"""
    client, db = await connect_to_mongo(mongo_url, database_name)

    try:
        # Limpar banco de dados se solicitado
        if clean:
            await clean_database(db)

        # Gerar dados
        print(f"Gerando {movies_count} filmes...")
        movies_data = generate_movies(movies_count)

        print(f"Gerando {users_count} usuários...")
        users_data = generate_users(users_count)

        print(f"Gerando {reviews_count} avaliações...")
        reviews_data = generate_reviews(users_data, movies_data, reviews_count)

        # Inserir dados
        print("Inserindo dados no MongoDB...")
        result_movies = await db.movies.insert_many(movies_data)
        print(f"Inseridos {len(result_movies.inserted_ids)} filmes no banco de dados.")

        result_users = await db.users.insert_many(users_data)
        print(f"Inseridos {len(result_users.inserted_ids)} usuários no banco de dados.")

        result_reviews = await db.reviews.insert_many(reviews_data)
        print(
            f"Inseridas {len(result_reviews.inserted_ids)} avaliações no banco de dados."
        )

        # Criar índices
        await create_indexes(db)

        print("\nCarregamento de dados concluído com sucesso!")

    except Exception as e:
        print(f"Erro ao carregar dados: {str(e)}")
    finally:
        await close_mongo_connection(client)


def main():
    parser = argparse.ArgumentParser(description="Carregar dados de teste no MongoDB")
    parser.add_argument(
        "--mongo-url",
        default="mongodb://localhost:27017",
        help="URL de conexão com o MongoDB (default: mongodb://localhost:27017)",
    )
    parser.add_argument(
        "--database",
        default="myfastapidb",
        help="Nome do banco de dados (default: myfastapidb)",
    )
    parser.add_argument(
        "--movies",
        type=int,
        default=50,
        help="Número de filmes a serem gerados (default: 50)",
    )
    parser.add_argument(
        "--users",
        type=int,
        default=10,
        help="Número de usuários a serem gerados (default: 10)",
    )
    parser.add_argument(
        "--reviews",
        type=int,
        default=100,
        help="Número de avaliações a serem geradas (default: 100)",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Limpar coleções antes de inserir novos dados",
    )

    args = parser.parse_args()

    asyncio.run(
        load_data(
            args.mongo_url,
            args.database,
            args.movies,
            args.users,
            args.reviews,
            args.clean,
        )
    )


if __name__ == "__main__":
    main()
