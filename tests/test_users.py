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

    if db.es.indices.exists("users-index"):
        db.es.indices.delete("users-index")

    users_configs = {
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "username": {"type": "keyword"},
                "joined_at": {"type": "date", "format": "yyyy-MM-dd HH:mm:ss x"},
                "follows": {
                    "type": "nested",
                    "properties": {
                        "id": {"type": "keyword"},
                        "followed_at": {
                            "type": "date",
                            "format": "yyyy-MM-dd HH:mm:ss x",
                        },
                    },
                },
                "followers": {
                    "type": "nested",
                    "properties": {
                        "id": {"type": "keyword"},
                        "followed_at": {
                            "type": "date",
                            "format": "yyyy-MM-dd HH:mm:ss x",
                        },
                    },
                },
            }
        }
    }

    db.es.indices.create(index="users-index", body=users_configs)

    # test users
    testuser1 = "testuser1"
    db.es.create(
        "users-index",
        id=utils.generate_md5(testuser1),
        body={
            "id": utils.generate_md5(testuser1),
            "username": testuser1,
            "joined_at": utils.time_now(),
            "follows": [],
            "followers": [],
        },
    )

    testuser2 = "testuser2"
    db.es.create(
        "users-index",
        id=utils.generate_md5(testuser2),
        body={
            "id": utils.generate_md5(testuser2),
            "username": testuser2,
            "joined_at": utils.time_now(),
            "follows": [],
            "followers": [],
        },
    )

    testuser3 = "testuser3"
    db.es.create(
        "users-index",
        id=utils.generate_md5(testuser3),
        body={
            "id": utils.generate_md5(testuser3),
            "username": testuser3,
            "joined_at": utils.time_now(),
            "follows": [
                {
                    "id": utils.generate_md5("testuser4"),
                    "followed_at": "2022-05-09 19:07:03 -0300",
                }
            ],
            "followers": [
                {
                    "id": utils.generate_md5("testuser4"),
                    "followed_at": "2022-05-09 19:07:03 -0300",
                }
            ],
        },
    )

    testuser4 = "testuser4"
    db.es.create(
        "users-index",
        id=utils.generate_md5(testuser4),
        body={
            "id": utils.generate_md5(testuser4),
            "username": testuser4,
            "joined_at": utils.time_now(),
            "follows": [
                {
                    "id": utils.generate_md5(testuser3),
                    "followed_at": "2022-05-09 19:07:03 -0300",
                }
            ],
            "followers": [
                {
                    "id": utils.generate_md5(testuser3),
                    "followed_at": "2022-05-09 19:07:03 -0300",
                }
            ],
        },
    )

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

        testuser1_id = utils.generate_md5("testuser1")

        # get testuser1
        response = client.get(f"api/{version}/users/{testuser1_id}")
        expected_user = dict(response.json())

        assert expected_user["id"] == testuser1_id
        assert expected_user["username"] == "testuser1"
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

        username = "testuser1"
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

        testuser3_id = utils.generate_md5("testuser3")
        testuser4_id = utils.generate_md5("testuser4")

        response = client.delete(f"api/{version}/users/{testuser3_id}")
        expected_user = dict(response.json())

        assert expected_user["id"] == testuser3_id
        assert expected_user["username"] == "testuser3"
        assert expected_user["follows"] == []
        assert expected_user["followers"] == []
        assert response.status_code == 200

        # check if testuser4 document was updated as well
        response = client.get(f"api/{version}/users/{testuser4_id}")
        expected_user = dict(response.json())

        follows_users_ids = [item["id"] for item in expected_user["follows"]]
        followers_users_ids = [item["id"] for item in expected_user["followers"]]

        assert testuser3_id not in follows_users_ids
        assert testuser3_id not in followers_users_ids


class TestFollow:

    """
    Test follow an user.
    """

    def test_nonexistent_follower(self, version, client, setup_db):

        assert setup_db

        testuser2_id = utils.generate_md5("testuser2")

        response = client.put(f"api/{version}/users/nonexistent/follow/{testuser2_id}")
        expected_user = dict(response.json())

        assert expected_user == {}
        assert response.status_code == 404

    def test_nonexistent_followed(self, version, client, setup_db):

        assert setup_db

        testuser1_id = utils.generate_md5("testuser1")

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

    def test_expected(self, version, client, setup_db):

        assert setup_db

        testuser1_id = utils.generate_md5("testuser1")
        testuser2_id = utils.generate_md5("testuser2")

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

        testuser4_id = utils.generate_md5("testuser4")

        response = client.put(
            f"api/{version}/users/nonexistent/unfollow/{testuser4_id}"
        )
        expected_user = dict(response.json())

        assert expected_user == {}
        assert response.status_code == 404

    def test_nonexistent_followed(self, version, client, setup_db):

        assert setup_db

        testuser3_id = utils.generate_md5("testuser3")

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

    def test_expected(self, version, client, setup_db):

        assert setup_db

        testuser3_id = utils.generate_md5("testuser3")
        testuser4_id = utils.generate_md5("testuser4")

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
