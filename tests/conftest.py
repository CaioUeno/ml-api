import json

import db
import pytest
from core import utils
from fastapi import testclient
from main import app


# change version to test easily
@pytest.fixture
def version() -> str:
    return "v1"


@pytest.fixture
def client():
    return testclient.TestClient(app)


@pytest.fixture
def sentiment_setup_db() -> bool:

    # delete indices if they already exists
    if db.es.indices.exists("users-index"):
        db.es.indices.delete("users-index")

    if db.es.indices.exists("tweets-index"):
        db.es.indices.delete("tweets-index")

    # load their mapping and create them
    with open("db/mappings/users.json") as f:
        db.es.indices.create(index="users-index", body=json.load(f))

    with open("db/mappings/tweets.json") as f:
        db.es.indices.create(index="tweets-index", body=json.load(f))

    johndoe = "johndoe"
    db.es.create(
        "users-index",
        id=utils.generate_md5(johndoe),
        body={
            "id": utils.generate_md5(johndoe),
            "username": johndoe,
            "joined_at": utils.time_now(),
            "follows": [],
            "followers": [],
        },
    )

    tweet1 = "first tweet example #api"
    db.es.create(
        "tweets-index",
        id=utils.generate_md5(tweet1 + johndoe),
        body={
            "id": utils.generate_md5(tweet1 + johndoe),
            "author_id": utils.generate_md5(johndoe),
            "tweeted_at": "2022-05-01 14:18:09 -0300",
            "text": tweet1,
            "sentiment": 1,
            "hashtags": ["#api"],
            "retweets": [],
            "likes": [],
        },
    )

    tweet2 = "this is a negative example #api"
    db.es.create(
        "tweets-index",
        id=utils.generate_md5(tweet2 + johndoe),
        body={
            "id": utils.generate_md5(tweet2 + johndoe),
            "author_id": utils.generate_md5(johndoe),
            "tweeted_at": "2022-05-02 14:18:09 -0300",
            "text": tweet2,
            "sentiment": -1,
            "hashtags": ["#api"],
            "retweets": [],
            "likes": [],
        },
    )

    tweet3 = "neutral? #api"
    db.es.create(
        "tweets-index",
        id=utils.generate_md5(tweet3 + johndoe),
        body={
            "id": utils.generate_md5(tweet3 + johndoe),
            "author_id": utils.generate_md5(johndoe),
            "tweeted_at": "2022-05-03 14:18:09 -0300",
            "text": tweet3,
            "sentiment": 0,
            "hashtags": ["#api"],
            "retweets": [],
            "likes": [],
        },
    )

    db.es.indices.refresh("tweets-index")
    db.es.indices.refresh("users-index")

    return True


# setup database to keep tests independent
@pytest.fixture
def tweets_setup_db() -> bool:

    # delete indices if they already exists
    if db.es.indices.exists("users-index"):
        db.es.indices.delete("users-index")

    if db.es.indices.exists("tweets-index"):
        db.es.indices.delete("tweets-index")

    # load their mapping and create them
    with open("db/mappings/users.json") as f:
        db.es.indices.create(index="users-index", body=json.load(f))

    with open("db/mappings/tweets.json") as f:
        db.es.indices.create(index="tweets-index", body=json.load(f))

    # populate them

    johndoe = "johndoe"
    jerry = "jerry"

    db.es.create(
        "users-index",
        id=utils.generate_md5(johndoe),
        body={
            "id": utils.generate_md5(johndoe),
            "username": johndoe,
            "joined_at": utils.time_now(),
            "follows": [
                {
                    "id": utils.generate_md5(jerry),
                    "followed_at": "2022-05-09 19:07:03 -0300",
                }
            ],
            "followers": [
                {
                    "id": utils.generate_md5(jerry),
                    "followed_at": "2022-05-09 19:07:03 -0300",
                }
            ],
        },
    )

    db.es.create(
        "users-index",
        id=utils.generate_md5(jerry),
        body={
            "id": utils.generate_md5(jerry),
            "username": jerry,
            "joined_at": utils.time_now(),
            "follows": [
                {
                    "id": utils.generate_md5(johndoe),
                    "followed_at": "2022-05-09 19:07:03 -0300",
                }
            ],
            "followers": [
                {
                    "id": utils.generate_md5(johndoe),
                    "followed_at": "2022-05-09 19:07:03 -0300",
                }
            ],
        },
    )

    tweet1 = "first tweet example #api"
    db.es.create(
        "tweets-index",
        id=utils.generate_md5(tweet1 + johndoe),
        body={
            "id": utils.generate_md5(tweet1 + johndoe),
            "author_id": utils.generate_md5(johndoe),
            "tweeted_at": utils.time_now(),
            "text": tweet1,
            "sentiment": 0,
            "hashtags": ["#api"],
            "retweets": [
                {
                    "id": utils.generate_md5(jerry),
                    "retweeted_at": "2022-05-09 19:07:03 -0300",
                }
            ],
            "likes": [
                {
                    "id": utils.generate_md5(jerry),
                    "liked_at": "2022-05-09 19:07:03 -0300",
                }
            ],
        },
    )

    # retweet
    db.es.create(
        "tweets-index",
        id=utils.generate_md5(utils.generate_md5(tweet1 + johndoe) + jerry),
        body={
            "id": utils.generate_md5(utils.generate_md5(tweet1 + johndoe) + jerry),
            "user_id": utils.generate_md5(jerry),
            "referenced_at": utils.time_now(),
            "tweet_id": utils.generate_md5(tweet1 + johndoe),
        },
    )

    tweet2 = "second tweet example"
    db.es.create(
        "tweets-index",
        id=utils.generate_md5(tweet2 + jerry),
        body={
            "id": utils.generate_md5(tweet2 + jerry),
            "author_id": utils.generate_md5(jerry),
            "tweeted_at": utils.time_now(),
            "text": tweet2,
            "sentiment": 0,
            "hashtags": ["#api"],
            "retweets": [],
            "likes": [],
        },
    )

    db.es.indices.refresh("tweets-index")
    db.es.indices.refresh("users-index")

    return True


@pytest.fixture
def users_setup_db() -> bool:

    # delete indices if they already exists
    if db.es.indices.exists("users-index"):
        db.es.indices.delete("users-index")

    if db.es.indices.exists("tweets-index"):
        db.es.indices.delete("tweets-index")

    # load their mapping and create them
    with open("db/mappings/users.json") as f:
        db.es.indices.create(index="users-index", body=json.load(f))

    with open("db/mappings/tweets.json") as f:
        db.es.indices.create(index="tweets-index", body=json.load(f))

    # populate them

    johndoe = "johndoe"
    jerry = "jerry"
    josh = "josh"

    db.es.create(
        "users-index",
        id=utils.generate_md5(johndoe),
        body={
            "id": utils.generate_md5(johndoe),
            "username": johndoe,
            "joined_at": utils.time_now(),
            "follows": [],
            "followers": [
                {
                    "id": utils.generate_md5(jerry),
                    "followed_at": "2022-05-09 19:07:03 -0300",
                }
            ],
        },
    )

    db.es.create(
        "users-index",
        id=utils.generate_md5(jerry),
        body={
            "id": utils.generate_md5(jerry),
            "username": jerry,
            "joined_at": utils.time_now(),
            "follows": [
                {
                    "id": utils.generate_md5(johndoe),
                    "followed_at": "2022-05-09 19:07:03 -0300",
                }
            ],
            "followers": [
                {
                    "id": utils.generate_md5(josh),
                    "followed_at": "2022-05-09 19:07:03 -0300",
                }
            ],
        },
    )

    db.es.create(
        "users-index",
        id=utils.generate_md5(josh),
        body={
            "id": utils.generate_md5(josh),
            "username": josh,
            "joined_at": utils.time_now(),
            "follows": [
                {
                    "id": utils.generate_md5(jerry),
                    "followed_at": "2022-05-09 19:07:03 -0300",
                }
            ],
            "followers": [],
        },
    )

    tweet1 = "first tweet example #api"
    db.es.create(
        "tweets-index",
        id=utils.generate_md5(tweet1 + johndoe),
        body={
            "id": utils.generate_md5(tweet1 + johndoe),
            "author_id": utils.generate_md5(johndoe),
            "tweeted_at": utils.time_now(),
            "text": tweet1,
            "sentiment": 0,
            "hashtags": ["#api"],
            "retweets": [
                {
                    "id": utils.generate_md5(jerry),
                    "retweeted_at": "2022-05-09 19:07:03 -0300",
                }
            ],
            "likes": [
                {
                    "id": utils.generate_md5(jerry),
                    "liked_at": "2022-05-09 19:07:03 -0300",
                }
            ],
        },
    )

    # retweet
    db.es.create(
        "tweets-index",
        id=utils.generate_md5(utils.generate_md5(tweet1 + johndoe) + jerry),
        body={
            "id": utils.generate_md5(utils.generate_md5(tweet1 + johndoe) + jerry),
            "user_id": utils.generate_md5(jerry),
            "referenced_at": utils.time_now(),
            "tweet_id": utils.generate_md5(tweet1 + johndoe),
        },
    )

    tweet2 = "second tweet example"
    db.es.create(
        "tweets-index",
        id=utils.generate_md5(tweet2 + jerry),
        body={
            "id": utils.generate_md5(tweet2 + jerry),
            "author_id": utils.generate_md5(jerry),
            "tweeted_at": utils.time_now(),
            "text": tweet2,
            "sentiment": 0,
            "hashtags": ["#api"],
            "retweets": [],
            "likes": [],
        },
    )

    db.es.indices.refresh("tweets-index")
    db.es.indices.refresh("users-index")

    return True
