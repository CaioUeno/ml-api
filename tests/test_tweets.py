from core import utils


class TestGetTweetOrRetweet:

    """
    Test retrieve tweet (or retweet) by id.
    """

    def test_non_existent_tweet(self, version, client, tweets_setup_db):

        assert tweets_setup_db

        response = client.get(f"api/{version}/tweets/nonexistentid")
        expected_tweet = dict(response.json())

        assert expected_tweet == {}
        assert response.status_code == 404

    def test_tweet_main(self, version, client, tweets_setup_db):

        assert tweets_setup_db

        tweet_id = utils.generate_md5("first tweet example #api" + "johndoe")

        response = client.get(f"api/{version}/tweets/{tweet_id}")
        expected_tweet = dict(response.json())

        assert expected_tweet["id"] == tweet_id
        assert expected_tweet["author_id"] == utils.generate_md5("johndoe")
        assert expected_tweet["text"] == "first tweet example #api"
        assert response.status_code == 200

    def test_retweet_main(self, version, client, tweets_setup_db):

        assert tweets_setup_db

        retweet_id = utils.generate_md5(
            utils.generate_md5("first tweet example #api" + "johndoe") + "jerry"
        )

        response = client.get(f"api/{version}/tweets/{retweet_id}")
        expected_retweet = dict(response.json())

        assert expected_retweet["id"] == retweet_id
        assert expected_retweet["user_id"] == utils.generate_md5("jerry")
        assert expected_retweet["tweet_id"] == utils.generate_md5(
            "first tweet example #api" + "johndoe"
        )
        assert response.status_code == 200


class TestGetUserTweets:

    """
    Test retrieve tweet from an user id.
    """

    def test_nonexistent_user(self, version, client, tweets_setup_db):

        assert tweets_setup_db

        response = client.get(f"api/{version}/tweets/user/nonexistentid")
        expected_tweets_list = list(response.json())

        assert expected_tweets_list == []
        assert response.status_code == 404

    def test_main(self, version, client, tweets_setup_db):

        assert tweets_setup_db

        johndoe_id = utils.generate_md5("johndoe")

        response = client.get(f"api/{version}/tweets/user/{johndoe_id}")
        print(response.json())
        expected_tweets_list = response.json()

        assert len(expected_tweets_list) == 1
        assert all([tweet["author_id"] == johndoe_id for tweet in expected_tweets_list])
        assert response.status_code == 200


class TestPublishTweet:

    """
    Test publish a tweet.
    """

    def test_non_existent_user(self, version, client, tweets_setup_db):

        assert tweets_setup_db

        response = client.post(
            f"api/{version}/tweets/nonexistentid/tweet",
            json={"text": "new tweet example"},
        )
        expected_tweet = dict(response.json())

        assert expected_tweet == {}
        assert response.status_code == 404

    def test_empty_string(self, version, client, tweets_setup_db):

        assert tweets_setup_db

        johndoe_id = utils.generate_md5("johndoe")
        response = client.post(
            f"api/{version}/tweets/{johndoe_id}/tweet",
            json={"text": ""},
        )
        expected_tweet = dict(response.json())

        assert expected_tweet == {}
        assert response.status_code == 500

    def test_same_text(self, version, client, tweets_setup_db):

        assert tweets_setup_db

        johndoe_id = utils.generate_md5("johndoe")
        tweet_text = "first tweet example #api"

        response = client.post(
            f"api/{version}/tweets/{johndoe_id}/tweet",
            json={"text": tweet_text},
        )
        expected_tweet = dict(response.json())

        assert expected_tweet["id"] == utils.generate_md5(tweet_text + "johndoe")
        assert expected_tweet["author_id"] == johndoe_id
        assert expected_tweet["text"] == tweet_text
        assert response.status_code == 409

    def test_main(self, version, client, tweets_setup_db):

        assert tweets_setup_db

        jerry_id = utils.generate_md5("jerry")

        response = client.post(
            f"api/{version}/tweets/{jerry_id}/tweet",
            json={"text": "new tweet example"},
        )
        expected_tweet = dict(response.json())

        assert expected_tweet["author_id"] == jerry_id
        assert expected_tweet["text"] == "new tweet example"
        assert response.status_code == 201


class TestRetweet:

    """
    Test retweet.
    """

    def test_non_existent_user(self, version, client, tweets_setup_db):

        assert tweets_setup_db

        tweet_id = utils.generate_md5("first tweet example #api" + "johndoe")

        response = client.post(f"api/{version}/tweets/nonexistentid/retweet/{tweet_id}")
        expected_retweet = dict(response.json())

        assert expected_retweet == {}
        assert response.status_code == 404

    def test_non_existent_tweet(self, version, client, tweets_setup_db):

        assert tweets_setup_db

        user_id = utils.generate_md5("jerry")

        response = client.post(f"api/{version}/tweets/{user_id}/retweet/nonexistentid")
        expected_retweet = dict(response.json())

        assert expected_retweet == {}
        assert response.status_code == 404

    def test_neither_exist(self, version, client, tweets_setup_db):

        assert tweets_setup_db

        response = client.post(
            f"api/{version}/tweets/nonexistentid/retweet/nonexistentid"
        )
        expected_retweet = dict(response.json())

        assert expected_retweet == {}
        assert response.status_code == 404

    def test_author_retweet(self, version, client, tweets_setup_db):

        assert tweets_setup_db

        user_id = utils.generate_md5("johndoe")
        tweet_id = utils.generate_md5("first tweet example #api" + "johndoe")

        response = client.post(f"api/{version}/tweets/{user_id}/retweet/{tweet_id}")
        expected_retweet = dict(response.json())

        assert expected_retweet == {}
        assert response.status_code == 500

    def test_main(self, version, client, tweets_setup_db):

        assert tweets_setup_db

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

    """
    Test Like a tweet.
    """

    def test_non_existent_user(self, version, client, tweets_setup_db):

        assert tweets_setup_db

        tweet_id = utils.generate_md5("first tweet example #api" + "johndoe")

        response = client.post(f"api/{version}/tweets/nonexistentid/like/{tweet_id}")
        expected_tweet = dict(response.json())

        assert expected_tweet == {}
        assert response.status_code == 404

    def test_non_existent_tweet(self, version, client, tweets_setup_db):

        assert tweets_setup_db

        user_id = utils.generate_md5("jerry")

        response = client.post(f"api/{version}/tweets/{user_id}/like/nonexistentid")
        expected_tweet = dict(response.json())

        assert expected_tweet == {}
        assert response.status_code == 404

    def test_neither_exist(self, version, client, tweets_setup_db):

        assert tweets_setup_db

        response = client.post(f"api/{version}/tweets/nonexistentid/like/nonexistentid")
        expected_tweet = dict(response.json())

        assert expected_tweet == {}
        assert response.status_code == 404

    def test_like_retweet(self, version, client, tweets_setup_db):

        assert tweets_setup_db

        user_id = utils.generate_md5("johndoe")
        retweet_id = utils.generate_md5(
            utils.generate_md5("first tweet example #api" + "johndoe") + "jerry"
        )

        response = client.post(f"api/{version}/tweets/{user_id}/like/{retweet_id}")
        expected_tweet = dict(response.json())

        assert expected_tweet == {}
        assert response.status_code == 500

    def test_main(self, version, client, tweets_setup_db):

        assert tweets_setup_db

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

    """
    Test delete tweet (or retweet) by id.
    """

    def test_non_existent_tweet(self, version, client, tweets_setup_db):

        assert tweets_setup_db

        response = client.delete(f"api/{version}/tweets/nonexistentid")
        expected_tweet = dict(response.json())

        assert expected_tweet == {}
        assert response.status_code == 404

    def test_tweet_main(self, version, client, tweets_setup_db):

        assert tweets_setup_db

        tweet_id = utils.generate_md5("first tweet example #api" + "johndoe")

        response = client.delete(f"api/{version}/tweets/{tweet_id}")
        expected_tweet = dict(response.json())

        assert expected_tweet["id"] == tweet_id
        assert response.status_code == 200

        retweet_id = utils.generate_md5(
            utils.generate_md5("first tweet example #api" + "johndoe") + "jerry"
        )

        response = client.get(f"api/{version}/tweets/{retweet_id}")
        expected_retweet = dict(response.json())

        assert expected_retweet == {}
        assert response.status_code == 404

    def test_retweet_main(self, version, client, tweets_setup_db):

        assert tweets_setup_db

        retweet_id = utils.generate_md5(
            utils.generate_md5("first tweet example #api" + "johndoe") + "jerry"
        )

        response = client.delete(f"api/{version}/tweets/{retweet_id}")
        expected_retweet = dict(response.json())

        assert expected_retweet["id"] == retweet_id
        assert response.status_code == 200
