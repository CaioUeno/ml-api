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


class TestGetUser:

    """
    Test retrieve user by id.
    """

    def test_nonexistent_user(self, version, client, setup_db):

        assert setup_db

        response = client.get(f"api/{version}/users/nonexistent")
        expected_user = dict(response.json())

        assert expected_user == {}
        assert response.status_code == 404

    def test_expected(self, version, client, setup_db):

        assert setup_db

        testuser1_id = utils.generate_md5("johndoe")

        # get testuser1
        response = client.get(f"api/{version}/users/{testuser1_id}")
        expected_user = dict(response.json())

        assert expected_user["id"] == testuser1_id
        assert expected_user["username"] == "johndoe"
        assert response.status_code == 200


class TestCreateUser:

    """
    Test create a new user.
    """

    def test_invalid_name(self, version, client, setup_db):

        assert setup_db

        # username with invalid chars
        invalid_username = "caio!@@#"

        response = client.post(
            f"api/{version}/users/", json={"username": invalid_username}
        )
        expected_user = dict(response.json())

        assert expected_user == {}
        assert response.status_code == 400

    def test_expected(self, version, client, setup_db):

        assert setup_db

        username = "".join(random.sample("abcdefghijklmnopqrstuvxwyz", 5))
        idd = utils.generate_md5(username)

        response = client.post(f"api/{version}/users/", json={"username": username})
        expected_user = dict(response.json())

        assert expected_user["id"] == idd
        assert expected_user["username"] == username
        assert response.status_code == 201

    def test_existent_user(self, version, client, setup_db):

        assert setup_db

        username = "johndoe"
        idd = utils.generate_md5(username)

        response = client.post(f"api/{version}/users/", json={"username": username})
        expected_user = dict(response.json())

        assert expected_user["id"] == idd
        assert expected_user["username"] == username
        assert response.status_code == 409


class TestDeleteUser:

    """
    Test delete an user.
    """

    def test_nonexistent_user(self, version, client, setup_db):

        assert setup_db

        response = client.delete(f"api/{version}/users/nonexistent")
        expected_user = dict(response.json())

        assert expected_user == {}
        assert response.status_code == 404

    def test_expected(self, version, client, setup_db):

        assert setup_db

        testuser3_id = utils.generate_md5("jerry")

        response = client.delete(f"api/{version}/users/{testuser3_id}")
        expected_user = dict(response.json())

        assert expected_user["id"] == testuser3_id
        assert expected_user["username"] == "jerry"
        assert expected_user["follows"] == []
        assert expected_user["followers"] == []
        assert response.status_code == 200

        # check if followers and who jerry followed were updated as well

        response = client.get(f"api/{version}/users/{utils.generate_md5('johndoe')}")
        expected_user = dict(response.json())

        followers_users_ids = [item["id"] for item in expected_user["followers"]]
        assert utils.generate_md5("johndoe") not in followers_users_ids

        response = client.get(f"api/{version}/users/{utils.generate_md5('josh')}")
        expected_user = dict(response.json())

        follows_users_ids = [item["id"] for item in expected_user["follows"]]
        assert utils.generate_md5("johndoe") not in follows_users_ids

        # check if tweets and retweets were deleted as well
        response = client.get(
            f"api/{version}/tweets/{utils.generate_md5('second tweet example' + 'jerry')}"
        )
        expected_tweet = dict(response.json())

        assert expected_tweet == {}
        assert response.status_code == 404

        response = client.get(
            f"api/{version}/tweets/{utils.generate_md5(utils.generate_md5('first tweet example #api' + 'johndoe') + 'jerry')}"
        )
        expected_retweet = dict(response.json())

        assert expected_retweet == {}
        assert response.status_code == 404

        response = client.get(
            f"api/{version}/tweets/{utils.generate_md5('first tweet example #api' + 'johndoe')}"
        )
        expected_tweet = dict(response.json())

        retweets_users_ids = [item["id"] for item in expected_tweet["retweets"]]
        likes_users_ids = [item["id"] for item in expected_tweet["likes"]]

        assert utils.generate_md5("jerry") not in retweets_users_ids
        assert utils.generate_md5("jerry") not in likes_users_ids


class TestFollow:

    """
    Test follow an user.
    """

    def test_nonexistent_follower(self, version, client, setup_db):

        assert setup_db

        testuser2_id = utils.generate_md5("jerry")

        response = client.put(f"api/{version}/users/nonexistent/follow/{testuser2_id}")
        expected_user = dict(response.json())

        assert expected_user == {}
        assert response.status_code == 404

    def test_nonexistent_followed(self, version, client, setup_db):

        assert setup_db

        testuser1_id = utils.generate_md5("johndoe")

        response = client.put(f"api/{version}/users/{testuser1_id}/follow/nonexistent")
        expected_user = dict(response.json())

        assert expected_user["id"] == testuser1_id
        assert response.status_code == 404

    def test_neither_exist(self, version, client, setup_db):

        assert setup_db

        response = client.put(f"api/{version}/users/nonexistent1/follow/nonexistent2")
        expected_user = dict(response.json())

        assert expected_user == {}
        assert response.status_code == 404

    def test_following_themselves(self, version, client, setup_db):

        assert setup_db

        testuser1_id = utils.generate_md5("johndoe")

        response = client.put(
            f"api/{version}/users/{testuser1_id}/follow/{testuser1_id}"
        )
        expected_user = dict(response.json())

        assert expected_user == {}
        assert response.status_code == 500

    def test_expected(self, version, client, setup_db):

        assert setup_db

        testuser1_id = utils.generate_md5("johndoe")
        testuser2_id = utils.generate_md5("jerry")

        response = client.put(
            f"api/{version}/users/{testuser1_id}/follow/{testuser2_id}"
        )
        expected_user = dict(response.json())

        follow_users_ids = [item["id"] for item in expected_user["follows"]]

        assert expected_user["id"] == testuser1_id
        assert testuser2_id in follow_users_ids
        assert response.status_code == 200

        # check if testuser2 document was updated as well
        response = client.get(f"api/{version}/users/{testuser2_id}")
        expected_user = dict(response.json())

        followers_users_ids = [item["id"] for item in expected_user["followers"]]

        assert testuser1_id in followers_users_ids


class TestUnfollow:

    """
    Test unfollow an user.
    """

    def test_nonexistent_follower(self, version, client, setup_db):

        assert setup_db

        testuser4_id = utils.generate_md5("johndoe")

        response = client.put(
            f"api/{version}/users/nonexistent/unfollow/{testuser4_id}"
        )
        expected_user = dict(response.json())

        assert expected_user == {}
        assert response.status_code == 404

    def test_nonexistent_followed(self, version, client, setup_db):

        assert setup_db

        testuser3_id = utils.generate_md5("jerry")

        response = client.put(
            f"api/{version}/users/{testuser3_id}/unfollow/nonexistent"
        )
        expected_user = dict(response.json())

        assert expected_user["id"] == testuser3_id
        assert response.status_code == 404

    def test_neither_exist(self, version, client, setup_db):

        assert setup_db

        response = client.put(f"api/{version}/users/nonexistent1/unfollow/nonexistent2")
        expected_user = dict(response.json())

        assert expected_user == {}
        assert response.status_code == 404

    def test_unfollowing_themselves(self, version, client, setup_db):

        assert setup_db

        testuser3_id = utils.generate_md5("jerry")

        response = client.put(
            f"api/{version}/users/{testuser3_id}/unfollow/{testuser3_id}"
        )
        expected_user = dict(response.json())

        assert expected_user == {}
        assert response.status_code == 500

    def test_expected(self, version, client, setup_db):

        assert setup_db

        testuser3_id = utils.generate_md5("jerry")
        testuser4_id = utils.generate_md5("johndoe")

        response = client.put(
            f"api/{version}/users/{testuser3_id}/unfollow/{testuser4_id}"
        )
        expected_user = dict(response.json())

        follow_users_ids = [item["id"] for item in expected_user["follows"]]

        assert expected_user["id"] == testuser3_id
        assert testuser4_id not in follow_users_ids
        assert response.status_code == 200

        # check if testuser2 document was updated as well
        response = client.get(f"api/{version}/users/{testuser4_id}")
        expected_user = dict(response.json())

        followers_users_ids = [item["id"] for item in expected_user["followers"]]

        assert testuser3_id not in followers_users_ids
