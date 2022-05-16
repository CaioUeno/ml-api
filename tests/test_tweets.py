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

    return True


class TestGetTweetOrRetweet:
    def test_non_existent_tweet(self, version, client, setup_db):

        assert setup_db

        response = client.get(f"api/{version}/tweets/nonexistentid")
        expected_tweet = dict(response.json())

        assert expected_tweet == {}
        assert response.status_code == 404

    def test_tweet_expected(self, version, client, setup_db):

        assert setup_db

        idd = utils.generate_md5("first tweet example #api" + "johndoe")

        response = client.get(f"api/{version}/tweets/{idd}")
        expected_tweet = dict(response.json())

        assert expected_tweet["id"] == idd
        assert expected_tweet["author_id"] == utils.generate_md5("johndoe")
        assert expected_tweet["text"] == "first tweet example #api"
        assert response.status_code == 200

    def test_retweet_expected(self, version, client, setup_db):

        assert setup_db

        idd = utils.generate_md5(
            utils.generate_md5("first tweet example #api" + "johndoe") + "jerry"
        )

        response = client.get(f"api/{version}/tweets/{idd}")
        expected_retweet = dict(response.json())

        assert expected_retweet["id"] == idd
        assert expected_retweet["user_id"] == utils.generate_md5("jerry")
        assert expected_retweet["tweet_id"] == utils.generate_md5(
            "first tweet example #api" + "johndoe"
        )
        assert response.status_code == 200


# class TestGetUserTweets:
#     def test_nonexistent_user(self, version, client, setup_db):

#         assert setup_db

#         response = client.get(f"api/{version}/tweets/user/nonexistentid")
#         expected_tweets_list = list(response.json())

#         assert expected_tweets_list == []
#         assert response.status_code == 404

#     def test_expected(self, version, client, setup_db):

#         assert setup_db

#         idd = utils.generate_md5("johndoe")

#         response = client.get(f"api/{version}/tweets/user/{idd}")
#         print(response.json())
#         expected_tweets_list = response.json()

#         assert len(expected_tweets_list) == 1
#         assert all([tweet["author_id"] == idd for tweet in expected_tweets_list])
#         assert response.status_code == 200


# # def test_get_user_timeline():

# #     response = client.get(f"api/v1/tweets/{utils.generate_md5('testuser2')}/timeline")
# #     docs = list(response.json())


class TestPublishTweet:
    def test_non_existent_user(self, version, client, setup_db):

        assert setup_db

        response = client.post(
            f"api/{version}/tweets/nonexistentid/tweet",
            json={"text": "new tweet example"},
        )
        expected_tweet = dict(response.json())

        assert expected_tweet == {}
        assert response.status_code == 404

    def test_same_text(self, version, client, setup_db):
        assert setup_db

        idd = utils.generate_md5("johndoe")
        response = client.post(
            f"api/{version}/tweets/{idd}/tweet",
            json={"text": "first tweet example #api"},
        )
        expected_tweet = dict(response.json())
        print(expected_tweet)
        assert expected_tweet["id"] == utils.generate_md5(
            "first tweet example #api" + "johndoe"
        )
        assert expected_tweet["author_id"] == utils.generate_md5("johndoe")
        assert expected_tweet["text"] == "first tweet example #api"
        assert response.status_code == 409

    def test_expected(self, version, client, setup_db):

        assert setup_db

        idd = utils.generate_md5("jerry")

        response = client.post(
            f"api/{version}/tweets/{idd}/tweet",
            json={"text": "new tweet example"},
        )
        expected_tweet = dict(response.json())

        assert expected_tweet["author_id"] == utils.generate_md5("jerry")
        assert expected_tweet["text"] == "new tweet example"
        assert response.status_code == 201


class TestRetweet:
    def test_non_existent_user(self, version, client, setup_db):

        assert setup_db

        tweet_id = utils.generate_md5("first tweet example #api" + "johndoe")

        response = client.post(f"api/{version}/tweets/nonexistentid/retweet/{tweet_id}")
        expected_retweet = dict(response.json())

        assert expected_retweet == {}
        assert response.status_code == 404

    def test_non_existent_tweet(self, version, client, setup_db):

        assert setup_db

        user_id = utils.generate_md5("jerry")

        response = client.post(f"api/{version}/tweets/{user_id}/retweet/nonexistentid")
        expected_retweet = dict(response.json())

        assert expected_retweet == {}
        assert response.status_code == 404

    def test_neither_exist(self, version, client, setup_db):

        assert setup_db

        response = client.post(
            f"api/{version}/tweets/nonexistentid/retweet/nonexistentid"
        )
        expected_retweet = dict(response.json())

        assert expected_retweet == {}
        assert response.status_code == 404

    def test_author_retweet(self, version, client, setup_db):

        assert setup_db

        user_id = utils.generate_md5("johndoe")
        tweet_id = utils.generate_md5("first tweet example #api" + "johndoe")

        response = client.post(f"api/{version}/tweets/{user_id}/retweet/{tweet_id}")
        expected_retweet = dict(response.json())

        assert expected_retweet == {}
        assert response.status_code == 500

    def test_expected(self, version, client, setup_db):

        assert setup_db

        user_id = utils.generate_md5("johndoe")
        tweet_id = utils.generate_md5("second tweet example" + "jerry")

        response = client.post(f"api/{version}/tweets/{user_id}/retweet/{tweet_id}")
        expected_retweet = dict(response.json())

        assert expected_retweet["id"] == utils.generate_md5(tweet_id + user_id)
        assert response.status_code == 201

        response = client.get(f"api/{version}/tweets/{tweet_id}")
        expected_tweet = dict(response.json())

        assert len(expected_tweet["retweets"]) == 1
        assert expected_tweet["retweets"][0]["id"] == user_id


class TestLikeTweet:
    def test_non_existent_user(self, version, client, setup_db):

        assert setup_db

        tweet_id = utils.generate_md5("first tweet example #api" + "johndoe")

        response = client.post(f"api/{version}/tweets/nonexistentid/like/{tweet_id}")
        expected_tweet = dict(response.json())

        assert expected_tweet == {}
        assert response.status_code == 404

    def test_non_existent_tweet(self, version, client, setup_db):

        assert setup_db

        user_id = utils.generate_md5("jerry")

        response = client.post(f"api/{version}/tweets/{user_id}/like/nonexistentid")
        expected_tweet = dict(response.json())

        assert expected_tweet == {}
        assert response.status_code == 404

    def test_neither_exist(self, version, client, setup_db):

        assert setup_db

        response = client.post(f"api/{version}/tweets/nonexistentid/like/nonexistentid")
        expected_tweet = dict(response.json())

        assert expected_tweet == {}
        assert response.status_code == 404

    def test_like_retweet(self, version, client, setup_db):

        assert setup_db

        user_id = utils.generate_md5("johndoe")
        retweet_id = utils.generate_md5(
            utils.generate_md5("first tweet example #api" + "johndoe") + "jerry"
        )

        response = client.post(f"api/{version}/tweets/{user_id}/like/{retweet_id}")
        expected_tweet = dict(response.json())

        assert expected_tweet == {}
        assert response.status_code == 500

    def test_expected(self, version, client, setup_db):

        assert setup_db

        user_id = utils.generate_md5("johndoe")
        tweet_id = utils.generate_md5("second tweet example" + "jerry")

        response = client.post(f"api/{version}/tweets/{user_id}/like/{tweet_id}")
        expected_tweet = dict(response.json())

        assert expected_tweet["id"] == tweet_id
        assert response.status_code == 201

        response = client.get(f"api/{version}/tweets/{tweet_id}")
        expected_tweet = dict(response.json())

        assert len(expected_tweet["likes"]) == 1
        assert expected_tweet["likes"][0]["id"] == user_id


class TestDeleteTweetOrRetweet:

    def test_non_existent_tweet(self, version, client, setup_db):

        assert setup_db

        response = client.delete(f"api/{version}/tweets/nonexistentid")
        expected_tweet = dict(response.json())

        assert expected_tweet == {}
        assert response.status_code == 404

    def test_tweet_expected(self, version, client, setup_db):

        assert setup_db

        tweet_id = utils.generate_md5("first tweet example #api" + "johndoe")

        response = client.delete(f"api/{version}/tweets/{tweet_id}")
        expected_tweet = dict(response.json())

        assert expected_tweet["id"] == tweet_id
        assert response.status_code == 200

    
    def test_retweet_expected(self, version, client, setup_db):

        assert setup_db

        retweet_id = utils.generate_md5(
            utils.generate_md5("first tweet example #api" + "johndoe") + "jerry"
        )

        response = client.delete(f"api/{version}/tweets/{retweet_id}")
        expected_retweet = dict(response.json())

        assert expected_retweet["id"] == retweet_id
        assert response.status_code == 200