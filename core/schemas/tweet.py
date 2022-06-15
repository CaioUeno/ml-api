from typing import List
from pydantic import BaseModel

from core.schemas import user

# error and not found
class EmptyTweet(BaseModel):
    pass


# error and not found
class EmptyReferenceTweet(BaseModel):
    pass


# complete retweet (as in the database)
class ReferenceTweet(BaseModel):
    id: str
    user_id: str
    referenced_at: str
    tweet_id: str


# complete tweet (as in the database)
class Tweet(BaseModel):
    id: str
    author_id: str
    tweeted_at: str
    text: str
    sentiment: int
    confidence: float
    hashtags: List[str]
    retweets: List[user.RetweetUser]
    likes: List[user.LikeUser]


# handles the input for a new tweet
class NewTweet(BaseModel):
    text: str
