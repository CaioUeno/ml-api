import json
import random
import pytest
from core import utils
from fastapi import testclient
from main import app
import db


# change version to test easily
@pytest.fixture
def version() -> str:
    return "v1"


@pytest.fixture
def client():
    return testclient.TestClient(app)


# setup database to keep tests independent
@pytest.fixture
def setup_db() -> bool:

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
            "tweeted_at": utils.time_now(),
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
            "tweeted_at": utils.time_now(),
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
            "tweeted_at": utils.time_now(),
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


class TestClassify:
    def test_empty_text(self, version, client, setup_db):

        assert setup_db

        response = client.post(f"api/{version}/sentiment/classify", json={"text": ""})
        expected_classification = dict(response.json())

        assert expected_classification == {"text": ""}
        assert response.status_code == 500

    def test_expected(self, version, client, setup_db):

        assert setup_db

        response = client.post(
            f"api/{version}/sentiment/classify", json={"text": "what a nice day"}
        )
        expected_classification = dict(response.json())

        assert "text" in expected_classification.keys()
        assert "sentiment" in expected_classification.keys()
        assert response.status_code == 200


class TestQuantifyUser:
    def test_non_existent_user(self, version, client, setup_db):

        assert setup_db

        response = client.post(f"api/{version}/sentiment/quantify/user/nonexistent")
        expected_prevalence = dict(response.json())

        assert expected_prevalence == {}
        assert response.status_code == 404

    def test_expected(self, version, client, setup_db):

        assert setup_db

        user_id = utils.generate_md5("johndoe")

        response = client.post(f"api/{version}/sentiment/quantify/user/{user_id}?date_from=0&date_to=10")
        expected_prevalence = dict(response.json())

        assert "negative" in expected_prevalence.keys()
        assert "neutral" in expected_prevalence.keys()
        assert "positive" in expected_prevalence.keys()
        assert response.status_code == 200


class TestClassifyHashtag:
    def test_non_existent_hashtag(self, version, client, setup_db):

        assert setup_db

        response = client.post(f"api/{version}/sentiment/quantify/hashtag/friday")
        expected_prevalence = dict(response.json())

        assert expected_prevalence == {}
        assert response.status_code == 200

    def test_expected(self, version, client, setup_db):

        assert setup_db

        response = client.post(f"api/{version}/sentiment/quantify/hashtag/api")
        expected_prevalence = dict(response.json())
        print(expected_prevalence)
        assert "negative" in expected_prevalence.keys()
        assert "neutral" in expected_prevalence.keys()
        assert "positive" in expected_prevalence.keys()
        assert response.status_code == 200
