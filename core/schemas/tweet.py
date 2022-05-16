from typing import List, Optional
from pydantic import BaseModel

from core.schemas import user


class BaseTweet(BaseModel):
    id: str


class ReferenceTweet(BaseTweet):
    user_id: str
    referenced_at: str
    tweet_id: str

class NotFoundTweet(BaseModel):
    pass

class EmptyTweet(BaseModel):
    pass

class EmptyReferenceTweet(BaseModel):
    pass

class Tweet(BaseTweet):
    author_id: str
    tweeted_at: str
    text: str
    sentiment: int
    hashtags: List[str]
    retweets: List[user.RetweetUser]
    likes: List[user.LikeUser]


class NewTweet(BaseModel):
    text: str
