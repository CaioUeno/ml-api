from core import utils
from fastapi import testclient
from main import app

client = testclient.TestClient(app)


def test_get_user():

    # get testuser1
    response = client.get(f"api/v1/users/{utils.generate_md5('testuser1')}")
    doc = dict(response.json())

    assert doc["id"] == utils.generate_md5("testuser1")
    assert doc["username"] == "testuser1"
    assert response.status_code == 200

    # non existing id
    response = client.get(f"api/v1/users/notexistingid")
    doc = dict(response.json())

    assert doc == {}
    assert response.status_code == 404


def test_create_user():

    # try to create an user with invalid chars
    response = client.post("api/v1/users/", json={"username": "caio!"})
    doc = dict(response.json())

    assert doc == {}
    assert response.status_code == 400

    # create an user caioueno
    response = client.post("api/v1/users/", json={"username": "caioueno"})
    doc = dict(response.json())

    assert doc["id"] == utils.generate_md5("caioueno")
    assert doc["username"] == "caioueno"
    assert response.status_code == 201

    # try to create the same user again
    response = client.post("api/v1/users/", json={"username": "caioueno"})
    doc = dict(response.json())

    assert doc["id"] == utils.generate_md5("caioueno")
    assert doc["username"] == "caioueno"
    assert response.status_code == 409


def test_delete_user():

    # try to delete non existing user
    response = client.delete(f"api/v1/users/notexistingid")
    doc = dict(response.json())

    assert doc == {}
    assert response.status_code == 404

    # delete an existing user
    response = client.delete(f"api/v1/users/{utils.generate_md5('caioueno')}")
    doc = dict(response.json())

    assert doc["id"] == utils.generate_md5("caioueno")
    assert doc["username"] == "caioueno"
    assert response.status_code == 200


def test_follow():

    # user who wants to follow doesn't exists
    response = client.put(
        f"api/v1/users/nonexistingid/follow/{utils.generate_md5('testuser2')}"
    )

    doc = dict(response.json())

    assert doc == {}
    assert response.status_code == 404

    # user to follow doesn't exists
    response = client.put(
        f"api/v1/users/{utils.generate_md5('testuser1')}/follow/nonexistingid"
    )

    doc = dict(response.json())

    assert doc == {}
    assert response.status_code == 404

    # neither users exists
    response = client.put(f"api/v1/users/nonexistingid/follow/nonexistingid2")

    doc = dict(response.json())

    assert doc == {}
    assert response.status_code == 404

    # expected
    response = client.put(
        f"api/v1/users/{utils.generate_md5('testuser1')}/follow/{utils.generate_md5('testuser2')}"
    )
    testuser1 = dict(response.json())

    follow_users_ids = [item["id"] for item in testuser1["follows"]]

    assert testuser1["id"] == utils.generate_md5("testuser1")
    assert utils.generate_md5("testuser2") in follow_users_ids
    assert response.status_code == 200

    response = client.get(f"api/v1/users/{utils.generate_md5('testuser2')}")
    testuser2 = dict(response.json())
    followers_users_ids = [item["id"] for item in testuser2["followers"]]

    assert utils.generate_md5("testuser1") in followers_users_ids


# def test_unfollow():

#     response = client.put(
#         f"api/v1/users/{utils.generate_md5('testuser1')}/unfollow/{utils.generate_md5('testuser2')}"
#     )
#     testuser1 = dict(response.json())
#     follow_users_ids = [item["id"] for item in testuser1["follows"]]

#     assert testuser1["id"] == utils.generate_md5("testuser1")
#     assert utils.generate_md5("testuser2") not in follow_users_ids
#     assert response.status_code == 200
