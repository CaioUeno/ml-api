from typing import Any, List

from core import utils
from core.schemas import tweet, user
from fastapi import APIRouter

router = APIRouter()


@router.get("/{tweet_id}", response_model=tweet.Tweet, status_code=200)
def get_tweet(tweet_id: str) -> Any:
    return NotImplementedError()


@router.get(
    "/user/{user_id}",
    response_model=List[tweet.Tweet],
    status_code=200,
)
def get_user_tweets(user_id: str) -> Any:
    return NotImplementedError()


@router.get(
    "/{user_id}/timeline",
    response_model=List[tweet.Tweet],
    status_code=200,
)
def get_user_timeline(user_id: str) -> Any:
    return NotImplementedError()


@router.post("/{user_id}/tweet", response_model=tweet.Tweet, status_code=201)
def publish_tweet(user_id: str, new_tweet: tweet.NewTweet) -> Any:
    return NotImplementedError()


@router.post(
    "/{user_id}/retweet/{tweet_id}",
    response_model=tweet.ReferenceTweet,
    status_code=201,
)
def retweet(user_id: str, tweet_id: str) -> Any:
    return NotImplementedError()


@router.put("/{user_id}/like/{tweet_id}", response_model=tweet.Tweet, status_code=200)
def like(user_id: str, tweet_id: str) -> Any:
    return NotImplementedError()


@router.delete("/{user_id}/{tweet_id}", status_code=200)
def delete_tweet(user_id: str, tweet_id: str) -> Any:
    return NotImplementedError()
