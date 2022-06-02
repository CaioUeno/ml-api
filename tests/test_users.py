import random

from core import utils


class TestGetUser:

    """
    Test retrieve user by id.
    """

    def test_nonexistent_user(self, version, client, users_setup_db):

        assert users_setup_db

        response = client.get(f"api/{version}/users/nonexistent")
        expected_user = dict(response.json())

        assert expected_user == {}
        assert response.status_code == 404

    def test_main(self, version, client, users_setup_db):

        assert users_setup_db

        testuser1_id = utils.generate_md5("johndoe")

        response = client.get(f"api/{version}/users/{testuser1_id}")
        expected_user = dict(response.json())

        assert expected_user["id"] == testuser1_id
        assert expected_user["username"] == "johndoe"
        assert response.status_code == 200


class TestCreateUser:

    """
    Test create a new user.
    """

    def test_null_name(self, version, client, users_setup_db):

        assert users_setup_db

        # username as empty string
        empty_string = ""

        response = client.post(f"api/{version}/users/", json={"username": empty_string})
        expected_user = dict(response.json())

        assert expected_user == {}
        assert response.status_code == 500

    def test_invalid_name(self, version, client, users_setup_db):

        assert users_setup_db

        # username with invalid chars
        invalid_username = "c4io!@@#"

        response = client.post(
            f"api/{version}/users/", json={"username": invalid_username}
        )
        expected_user = dict(response.json())

        assert expected_user == {}
        assert response.status_code == 500

    def test_existent_username(self, version, client, users_setup_db):

        assert users_setup_db

        existent_username = "johndoe"
        idd = utils.generate_md5(existent_username)

        response = client.post(
            f"api/{version}/users/", json={"username": existent_username}
        )
        expected_user = dict(response.json())

        assert expected_user["id"] == idd
        assert expected_user["username"] == existent_username
        assert response.status_code == 409

    def test_main(self, version, client, users_setup_db):

        assert users_setup_db

        username = "".join(random.sample("abcdefghijklmnopqrstuvxwyz", 5))
        idd = utils.generate_md5(username)

        response = client.post(f"api/{version}/users/", json={"username": username})
        expected_user = dict(response.json())

        assert expected_user["id"] == idd
        assert expected_user["username"] == username
        assert response.status_code == 201


class TestDeleteUser:

    """
    Test delete an user.
    """

    def test_nonexistent_user(self, version, client, users_setup_db):

        assert users_setup_db

        response = client.delete(f"api/{version}/users/nonexistent")
        expected_user = dict(response.json())

        assert expected_user == {}
        assert response.status_code == 404

    def test_main(self, version, client, users_setup_db):

        assert users_setup_db

        jerry_id = utils.generate_md5("jerry")

        response = client.delete(f"api/{version}/users/{jerry_id}")
        expected_user = dict(response.json())

        assert expected_user["id"] == jerry_id
        assert expected_user["username"] == "jerry"
        assert expected_user["follows"] == []
        assert expected_user["followers"] == []
        assert response.status_code == 200

        # check if followers and who jerry followed were updated as well
        ## check if jerry was removed from johndoe followers list
        johndoe_id = utils.generate_md5("johndoe")
        response = client.get(f"api/{version}/users/{johndoe_id}")
        expected_user = dict(response.json())

        followers_users_ids = [item["id"] for item in expected_user["followers"]]

        assert jerry_id not in followers_users_ids

        ## check if jerry was removed from josh follows list
        josh_id = utils.generate_md5("josh")
        response = client.get(f"api/{version}/users/{josh_id}")
        expected_user = dict(response.json())

        follows_users_ids = [item["id"] for item in expected_user["follows"]]

        assert jerry_id not in follows_users_ids

        # check if tweets and retweets were deleted as well
        ## check if tweet was deleted
        tweet_id = utils.generate_md5("second tweet example" + "jerry")
        response = client.get(f"api/{version}/tweets/{tweet_id}")
        expected_tweet = dict(response.json())

        assert expected_tweet == {}
        assert response.status_code == 404

        ## check if retweet was deleted - and if its original tweet updated
        retweet_id = utils.generate_md5(
            utils.generate_md5("first tweet example #api" + "johndoe") + "jerry"
        )
        response = client.get(f"api/{version}/tweets/{retweet_id}")
        expected_retweet = dict(response.json())

        assert expected_retweet == {}
        assert response.status_code == 404

        response = client.get(
            f"api/{version}/tweets/{utils.generate_md5('first tweet example #api' + 'johndoe')}"
        )
        expected_tweet = dict(response.json())

        retweets_users_ids = [item["id"] for item in expected_tweet["retweets"]]
        likes_users_ids = [item["id"] for item in expected_tweet["likes"]]

        assert jerry_id not in retweets_users_ids
        assert jerry_id not in likes_users_ids


class TestFollow:

    """
    Test follow an user.
    """

    def test_nonexistent_follower(self, version, client, users_setup_db):

        assert users_setup_db

        jerry_id = utils.generate_md5("jerry")

        response = client.put(f"api/{version}/users/nonexistent/follow/{jerry_id}")
        expected_user = dict(response.json())

        assert expected_user == {}
        assert response.status_code == 404

    def test_nonexistent_followed(self, version, client, users_setup_db):

        assert users_setup_db

        johndoe_id = utils.generate_md5("johndoe")

        response = client.put(f"api/{version}/users/{johndoe_id}/follow/nonexistent")
        expected_user = dict(response.json())

        assert expected_user["id"] == johndoe_id
        assert response.status_code == 404

    def test_neither_exist(self, version, client, users_setup_db):

        assert users_setup_db

        response = client.put(f"api/{version}/users/nonexistent1/follow/nonexistent2")
        expected_user = dict(response.json())

        assert expected_user == {}
        assert response.status_code == 404

    def test_following_themselves(self, version, client, users_setup_db):

        assert users_setup_db

        johndoe_id = utils.generate_md5("johndoe")

        response = client.put(f"api/{version}/users/{johndoe_id}/follow/{johndoe_id}")
        expected_user = dict(response.json())

        assert expected_user["id"] == johndoe_id
        assert response.status_code == 500

    def test_main(self, version, client, users_setup_db):

        assert users_setup_db

        johndoe_id = utils.generate_md5("johndoe")
        jerry_id = utils.generate_md5("jerry")

        response = client.put(f"api/{version}/users/{johndoe_id}/follow/{jerry_id}")
        expected_user = dict(response.json())

        follow_users_ids = [item["id"] for item in expected_user["follows"]]

        assert expected_user["id"] == johndoe_id
        assert jerry_id in follow_users_ids
        assert response.status_code == 200

        # check if testuser2 document was updated as well
        response = client.get(f"api/{version}/users/{jerry_id}")
        expected_user = dict(response.json())

        followers_users_ids = [item["id"] for item in expected_user["followers"]]

        assert johndoe_id in followers_users_ids


class TestUnfollow:

    """
    Test unfollow an user.
    """

    def test_nonexistent_follower(self, version, client, users_setup_db):

        assert users_setup_db

        johndoe_id = utils.generate_md5("johndoe")

        response = client.put(f"api/{version}/users/nonexistent/unfollow/{johndoe_id}")
        expected_user = dict(response.json())

        assert expected_user == {}
        assert response.status_code == 404

    def test_nonexistent_followed(self, version, client, users_setup_db):

        assert users_setup_db

        jerry_id = utils.generate_md5("jerry")

        response = client.put(f"api/{version}/users/{jerry_id}/unfollow/nonexistent")
        expected_user = dict(response.json())

        assert expected_user["id"] == jerry_id
        assert response.status_code == 404

    def test_neither_exist(self, version, client, users_setup_db):

        assert users_setup_db

        response = client.put(f"api/{version}/users/nonexistent1/unfollow/nonexistent2")
        expected_user = dict(response.json())

        assert expected_user == {}
        assert response.status_code == 404

    def test_unfollowing_themselves(self, version, client, users_setup_db):

        assert users_setup_db

        jerry_id = utils.generate_md5("jerry")

        response = client.put(f"api/{version}/users/{jerry_id}/unfollow/{jerry_id}")
        expected_user = dict(response.json())

        assert expected_user["id"] == jerry_id
        assert response.status_code == 500

    def test_main(self, version, client, users_setup_db):

        assert users_setup_db

        jerry_id = utils.generate_md5("jerry")
        johndoe_id = utils.generate_md5("johndoe")

        response = client.put(f"api/{version}/users/{jerry_id}/unfollow/{johndoe_id}")
        expected_user = dict(response.json())

        follow_users_ids = [item["id"] for item in expected_user["follows"]]

        assert expected_user["id"] == jerry_id
        assert johndoe_id not in follow_users_ids
        assert response.status_code == 200

        # check if testuser2 document was updated as well
        response = client.get(f"api/{version}/users/{johndoe_id}")
        expected_user = dict(response.json())

        followers_users_ids = [item["id"] for item in expected_user["followers"]]

        assert jerry_id not in followers_users_ids
