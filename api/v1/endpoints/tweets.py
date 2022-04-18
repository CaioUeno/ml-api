from typing import Any

from core import utils
from core.schemas import tweet, user
from fastapi import APIRouter

router = APIRouter()


@router.get("/{tweet_id}", response_model=tweet.Tweet)
def get_tweet(tweet_id: str) -> Any:

    fake_tweet = {
        "id": "sdfasdf",
        "author_id": "sdjfioa",
        "tweeted_at": utils.time_now(),
        "text": "asdfjhas @de @asdijf",
        "hastags": ["@de", "@asdijf"],
        "retweets": [],
        "likes": [],
    }

    return fake_tweet


@router.post("/{user_id}/tweet", response_model=tweet.Tweet)
def publish_tweet(user_id: str, new_tweet: tweet.NewTweet) -> Any:

    new_tweet = {
        "id": utils.generate_md5(user_id + new_tweet["text"] + utils.time_now()),
        "author_id": user_id,
        "tweeted_at": utils.time_now(),
        "text": new_tweet["text"],
        "hashtags": utils.extract_hashtags(new_tweet["text"]),
        "retweets": [],
        "likes": [],
    }

    return new_tweet


@router.post("/{user_id}/retweet/{tweet_id}", response_model=tweet.ReferenceTweet)
def retweet(user_id: str, tweet_id: str) -> Any:

    ref_tweet = {
        "id": utils.generate_md5(user_id + tweet_id + utils.time_now()),
        "user_id": user_id,
        "referenced_at": utils.time_now(),
        "tweet_id": tweet_id,
    }

    return ref_tweet


@router.post("/{user_id}/like/{tweet_id}", response_model=tweet.Tweet)
def like(user_id: str, tweet_id: str) -> Any:

    updated_tweet = {
        "id": "sdfasdf",
        "author_id": "sdjfioa",
        "tweeted_at": utils.time_now(),
        "text": "asdfjhas @de @asdijf",
        "hastags": ["@de", "@asdijf"],
        "retweets": [],
        "likes": [],
    }

    updated_tweet["likes"].append(user.LikeUser(id=user_id, liked_at=utils.time_now()))

    return updated_tweet


@router.delete("/{user_id}/{tweet_id}")
def delete_tweet(user_id: str, tweet_id: str) -> Any:

    fake_tweet = {
        "id": "sdfasdf",
        "author_id": "sdjfioa",
        "tweeted_at": utils.time_now(),
        "text": "asdfjhas @de @asdijf",
        "hastags": ["@de", "@asdijf"],
        "retweets": [],
        "likes": [],
    }

    return True
