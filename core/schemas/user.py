from typing import List
from pydantic import BaseModel


class NotFoundUser(BaseModel):
    pass

class EmptyUser(BaseModel):
    pass


class NewUser(BaseModel):
    username: str


class BaseReferenceUser(BaseModel):
    id: str


class FollowUser(BaseReferenceUser):
    followed_at: str


class RetweetUser(BaseReferenceUser):
    retweeted_at: str


class LikeUser(BaseReferenceUser):
    liked_at: str


class User(BaseModel):
    id: str
    username: str
    joined_at: str
    follows: List[FollowUser]
    followers: List[FollowUser]
