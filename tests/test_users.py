import random
import pytest
from core import utils
from fastapi import testclient
from main import app


# @pytest.fixture
# def version():
#     return "v1"


@pytest.fixture
def client():
    return testclient.TestClient(app)


@pytest.fixture
def setup_db(client):

    if client.indices.exists("users-index"):
        client.indices.delete("users-index")

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

    client.indices.create(index="users-index", body=users_configs)

    # test users
    testuser1 = "testuser1"
    client.create(
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
    client.create(
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
    client.create(
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
            "followers": [],
        },
    )

    testuser4 = "testuser4"
    client.create(
        "users-index",
        id=utils.generate_md5(testuser4),
        body={
            "id": utils.generate_md5(testuser4),
            "username": testuser4,
            "joined_at": utils.time_now(),
            "follows": [],
            "followers": [
                {
                    "id": utils.generate_md5(testuser3),
                    "followed_at": "2022-05-09 19:07:03 -0300",
                }
            ],
        },
    )


class TestGetUser:
    def test_nonexistent_user(self, client):

        response = client.get(f"api/v1/users/nonexistent")
        expected_user = dict(response.json())

        assert expected_user == {}
        assert response.status_code == 404

    def test_expected(self, client):

        testuser1_id = utils.generate_md5("testuser1")

        # get testuser1
        response = client.get(f"api/v1/users/{testuser1_id}")
        expected_user = dict(response.json())

        assert expected_user["id"] == testuser1_id
        assert expected_user["username"] == "testuser1"
        assert response.status_code == 200


class TestCreateUser:
    def test_invalid_name(self, client):

        # username with invalid chars
        invalid_username = "caio!@@#"

        response = client.post("api/v1/users/", json={"username": invalid_username})
        expected_user = dict(response.json())

        assert expected_user == {}
        assert response.status_code == 400

    def test_expected(self, client):

        username = "".join(random.sample("abcdefghijklmnopqrstuvxwyz", 5))
        idd = utils.generate_md5(username)

        response = client.post("api/v1/users/", json={"username": username})
        expected_user = dict(response.json())

        assert expected_user["id"] == idd
        assert expected_user["username"] == username
        assert response.status_code == 201

    def test_existent_user(self, client):

        username = "testuser1"
        idd = utils.generate_md5(username)

        response = client.post("api/v1/users/", json={"username": username})
        expected_user = dict(response.json())

        assert expected_user["id"] == idd
        assert expected_user["username"] == username
        assert response.status_code == 409


# class TestDeleteUser:
#     def test_nonexistent_user(self, client):

#         response = client.delete(f"api/v1/users/nonexistent")
#         doc = dict(response.json())

#         assert doc == {}
#         assert response.status_code == 404

#     def test_standard_behaviour(self, client):
#         response = client.delete(f"api/v1/users/{utils.generate_md5('caioueno')}")
#         doc = dict(response.json())

#         assert doc["id"] == utils.generate_md5("caioueno")
#         assert doc["username"] == "caioueno"
#         assert response.status_code == 200


class TestFollow:
    def test_nonexistent_follower(self, client):

        testuser2_id = utils.generate_md5("testuser2")

        response = client.put(f"api/v1/users/nonexistent/follow/{testuser2_id}")
        expected_user = dict(response.json())

        assert expected_user == {}
        assert response.status_code == 404

    def test_nonexistent_followed(self, client):

        testuser1_id = utils.generate_md5("testuser1")

        response = client.put(f"api/v1/users/{testuser1_id}/follow/nonexistent")
        expected_user = dict(response.json())

        assert expected_user["id"] == testuser1_id
        assert response.status_code == 404

    def test_neither_exist(self, client):

        response = client.put(f"api/v1/users/nonexistent1/follow/nonexistent2")
        expected_user = dict(response.json())

        assert expected_user == {}
        assert response.status_code == 404

    def test_expected(self, client):

        testuser1_id = utils.generate_md5("testuser1")
        testuser2_id = utils.generate_md5("testuser2")

        response = client.put(f"api/v1/users/{testuser1_id}/follow/{testuser2_id}")
        expected_user = dict(response.json())

        follow_users_ids = [item["id"] for item in expected_user["follows"]]

        assert expected_user["id"] == testuser1_id
        assert testuser2_id in follow_users_ids
        assert response.status_code == 200

        # check if testuser2 document was updated as well
        response = client.get(f"api/v1/users/{testuser2_id}")
        expected_user = dict(response.json())

        followers_users_ids = [item["id"] for item in expected_user["followers"]]

        assert testuser1_id in followers_users_ids


class TestUnfollow:
    def test_nonexistent_follower(self, client):

        testuser4_id = utils.generate_md5("testuser4")

        response = client.put(f"api/v1/users/nonexistent/unfollow/{testuser4_id}")
        expected_user = dict(response.json())

        assert expected_user == {}
        assert response.status_code == 404

    def test_nonexistent_followed(self, client):

        testuser3_id = utils.generate_md5("testuser3")

        response = client.put(f"api/v1/users/{testuser3_id}/unfollow/nonexistent")
        expected_user = dict(response.json())

        assert expected_user["id"] == testuser3_id
        assert response.status_code == 404

    def test_neither_exist(self, client):

        response = client.put(f"api/v1/users/nonexistent1/unfollow/nonexistent2")
        expected_user = dict(response.json())

        assert expected_user == {}
        assert response.status_code == 404

    def test_expected(self, client):

        testuser3_id = utils.generate_md5("testuser3")
        testuser4_id = utils.generate_md5("testuser4")

        response = client.put(f"api/v1/users/{testuser3_id}/unfollow/{testuser4_id}")
        expected_user = dict(response.json())

        print(expected_user)

        follow_users_ids = [item["id"] for item in expected_user["follows"]]

        assert expected_user["id"] == testuser3_id
        assert testuser4_id not in follow_users_ids
        assert response.status_code == 200

        # check if testuser2 document was updated as well
        response = client.get(f"api/v1/users/{testuser4_id}")
        expected_user = dict(response.json())

        followers_users_ids = [item["id"] for item in expected_user["followers"]]

        assert testuser3_id not in followers_users_ids
