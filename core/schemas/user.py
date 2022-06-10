from typing import List
from pydantic import BaseModel


# error or not found
class EmptyUser(BaseModel):
    pass


# even though the next three classes share "id" field (could use a shared parent class),
# it is more readable to replicate it on each class

# for both follows and followers fields
class FollowUser(BaseModel):
    id: str
    followed_at: str


class RetweetUser(BaseModel):
    id: str
    retweeted_at: str


class LikeUser(BaseModel):
    id: str
    liked_at: str


# complete user (as in the database)
class User(BaseModel):
    id: str
    username: str
    joined_at: str
    follows: List[FollowUser]
    followers: List[FollowUser]


# handles the input for a new user
class NewUser(BaseModel):
    username: str
