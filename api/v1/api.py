from fastapi import APIRouter
from api.v1.endpoints import users, tweets, sentiment

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(tweets.router, prefix="/tweets", tags=["tweets"])
api_router.include_router(sentiment.router, prefix="/sentiment", tags=["sentiment"])
