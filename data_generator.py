import os
import random
from datetime import datetime, timedelta
from bson import ObjectId
from faker import Faker
from motor.motor_asyncio import AsyncIOMotorClient

# Criar instância do Faker para gerar dados aleatórios
fake = Faker('pt_BR')

def generate_movies(count=50):
    """Gerar dados de filmes para teste"""
    # Dados para aumentar o realismo
    genres = [
        "Ação", "Aventura", "Animação", "Biografia", "Comédia", 
        "Crime", "Documentário", "Drama", "Família", "Fantasia", 
        "História", "Terror", "Musical", "Mistério", "Romance", 
        "Ficção Científica", "Thriller", "Guerra", "Faroeste"
    ]
    
    famous_directors = [
        "Steven Spielberg", "Martin Scorsese", "Christopher Nolan",
        "Quentin Tarantino", "James Cameron", "Ridley Scott",
        "Francis Ford Coppola", "Peter Jackson", "David Fincher",
        "Woody Allen", "Tim Burton", "Stanley Kubrick",
        "Alfred Hitchcock", "Clint Eastwood", "Spike Lee"
    ]
    
    famous_actors = [
        "Tom Hanks", "Leonardo DiCaprio", "Robert De Niro", "Meryl Streep",
        "Brad Pitt", "Johnny Depp", "Denzel Washington", "Morgan Freeman",
        "Jennifer Lawrence", "Sandra Bullock", "Scarlett Johansson", "Emma Stone",
        "Viola Davis", "Samuel L. Jackson", "Harrison Ford", "Tom Cruise",
        "Will Smith", "Keanu Reeves", "Anthony Hopkins", "Al Pacino",
        "Anne Hathaway", "Cate Blanchett", "Angelina Jolie", "Daniel Day-Lewis"
    ]
    
    # Lista de filmes conhecidos para adicionar à lista
    known_movies = [
        {
            "_id": ObjectId(),
            "title": "O Auto da Compadecida",
            "genres": ["Comédia", "Drama"],
            "director": "Guel Arraes",
            "actors": ["Selton Mello", "Matheus Nachtergaele", "Fernanda Montenegro"]
        },
        {
            "_id": ObjectId(),
            "title": "Cidade de Deus",
            "genres": ["Crime", "Drama"],
            "director": "Fernando Meirelles",
            "actors": ["Alexandre Rodrigues", "Leandro Firmino", "Matheus Nachtergaele"]
        },
        {
            "_id": ObjectId(),
            "title": "Tropa de Elite",
            "genres": ["Ação", "Crime", "Drama"],
            "director": "José Padilha",
            "actors": ["Wagner Moura", "André Ramiro", "Caio Junqueira"]
        },
        {
            "_id": ObjectId(),
            "title": "Central do Brasil",
            "genres": ["Drama"],
            "director": "Walter Salles",
            "actors": ["Fernanda Montenegro", "Vinícius de Oliveira", "Marília Pêra"]
        },
        {
            "_id": ObjectId(),
            "title": "Bacurau",
            "genres": ["Mistério", "Thriller", "Faroeste"],
            "director": "Kleber Mendonça Filho",
            "actors": ["Sônia Braga", "Udo Kier", "Bárbara Colen"]
        }
    ]
    
    # Começar com os filmes conhecidos
    movies = known_movies.copy()
    
    # Continuar a gerar até atingir o número desejado
    for i in range(len(movies), count):
        # Gerar um filme aleatório
        movie = {
            "_id": ObjectId(),
            "title": fake.catch_phrase(),
            "genres": random.sample(genres, random.randint(1, 3)),
            "director": random.choice(famous_directors),
            "actors": random.sample(famous_actors, random.randint(3, 6))
        }
        movies.append(movie)
    
    return movies

def generate_users(count=10):
    """Gerar dados de usuários para teste"""
    # Hash de senha mockado - em produção usaria bcrypt
    hashed_password = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # 'password'
    
    # Usuários de teste
    users = []
    
    # Gerar usuários adicionais
    for i in range(count):
        user = {
            "_id": ObjectId(),
            "username": fake.user_name(),
            "email": fake.email(),
            "password_hash": hashed_password,
            "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 60))
        }
        users.append(user)
    
    return users

def generate_reviews(users, movies, count=100):
    """Gerar dados de avaliações para teste"""
    # Comentários comuns para avaliações
    positive_comments = [
        "Excelente filme! Recomendo muito.",
        "Um dos melhores que já assisti.",
        "Ótima atuação e direção impecável.",
        "Roteiro surpreendente e bem executado.",
        "Adorei cada minuto, muito envolvente!"
    ]
    
    neutral_comments = [
        "Filme razoável, vale assistir uma vez.",
        "Teve bons momentos, mas também fracos.",
        "Esperava mais, mas não foi ruim.",
        "Uma história interessante, mas previsível.",
        "Entretenimento médio."
    ]
    
    negative_comments = [
        "Não recomendo, muito fraco.",
        "Desperdiçou um bom potencial.",
        "Roteiro confuso e atuações fracas.",
        "Faltou desenvolvimento dos personagens.",
        "Muito longo e pouco interessante."
    ]
    
    reviews = []
    evaluated_pairs = set()
    
    # Gerar avaliações aleatórias
    while len(reviews) < count:
        user = random.choice(users)
        movie = random.choice(movies)
        
        user_id = str(user["_id"])
        movie_id = str(movie["_id"])
        
        # Evitar duplicatas
        if (user_id, movie_id) in evaluated_pairs:
            continue
        
        # Gerar avaliação aleatória
        rating = round(random.uniform(1.0, 5.0) * 2) / 2  # Arredondar para incrementos de 0.5
        
        # Selecionar comentário baseado na avaliação
        if rating >= 4.0:
            comment = random.choice(positive_comments)
        elif rating >= 2.5:
            comment = random.choice(neutral_comments)
        else:
            comment = random.choice(negative_comments)
        
        # Criar avaliação
        review = {
            "_id": ObjectId(),
            "user_id": user_id,
            "movie_id": movie_id,
            "rating": rating,
            "comment": comment,
            "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 30))
        }
        
        # Adicionar à lista e ao conjunto de pares avaliados
        reviews.append(review)
        evaluated_pairs.add((user_id, movie_id))
    
    return reviews

async def connect_to_mongo(mongo_url, database_name):
    """Conectar ao MongoDB e retornar o cliente e o banco de dados"""
    client = AsyncIOMotorClient(mongo_url)
    db = client[database_name]
    return client, db

async def close_mongo_connection(client):
    """Fechar a conexão com o MongoDB"""
    client.close()
