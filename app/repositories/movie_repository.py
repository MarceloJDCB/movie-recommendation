from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.models.movie import Movie
from app.models.review import Review
from app.repositories.base_repository import BaseRepository


class MovieRepository(BaseRepository[Movie]):
    """
    Repositório para operações com filmes no MongoDB.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "movies", Movie)
        self.reviews_collection = db.reviews

    async def create_review(self, review: Review) -> Review:
        """Creates a new review in the database."""
        print(f"Creating review: {review}")
        document = review.to_dict()
        print(f"Review document before ID conversion: {document}")

        # Convert string IDs to ObjectId for MongoDB if needed
        if "user_id" in document and document["user_id"]:
            try:
                document["user_id"] = ObjectId(document["user_id"])
                print(f"Converted user_id to ObjectId: {document['user_id']}")
            except Exception as e:
                print(f"Failed to convert user_id to ObjectId: {e}")
                # Keep as string if not a valid ObjectId
                pass

        if "movie_id" in document and document["movie_id"]:
            try:
                document["movie_id"] = ObjectId(document["movie_id"])
                print(f"Converted movie_id to ObjectId: {document['movie_id']}")
            except Exception as e:
                print(f"Failed to convert movie_id to ObjectId: {e}")
                # Keep as string if not a valid ObjectId
                pass

        print(f"Document after ID conversion: {document}")
        result = await self.reviews_collection.insert_one(document)
        print(f"Insert result: {result.inserted_id}")

        created = await self.reviews_collection.find_one({"_id": result.inserted_id})
        print(f"Retrieved document from DB: {created}")

        # Convert ObjectIds back to strings before creating the Review object
        if "_id" in created:
            created["id"] = str(created["_id"])
            print(f"Converted _id to string id: {created['id']}")

        if "user_id" in created and isinstance(created["user_id"], ObjectId):
            created["user_id"] = str(created["user_id"])
            print(f"Converted user_id back to string: {created['user_id']}")

        if "movie_id" in created and isinstance(created["movie_id"], ObjectId):
            created["movie_id"] = str(created["movie_id"])
            print(f"Converted movie_id back to string: {created['movie_id']}")

        print(f"Final document before creating Review: {created}")
        return Review.from_dict(created)
