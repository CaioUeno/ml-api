from core import utils


class TestClassify:
    def test_empty_text(self, version, client, sentiment_setup_db):

        assert sentiment_setup_db

        response = client.post(f"api/{version}/sentiment/classify", json={"text": ""})
        expected_classification = dict(response.json())

        assert expected_classification == {"text": ""}
        assert response.status_code == 500

    def test_expected(self, version, client, sentiment_setup_db):

        assert sentiment_setup_db

        response = client.post(
            f"api/{version}/sentiment/classify", json={"text": "what a nice day"}
        )
        expected_classification = dict(response.json())

        assert "text" in expected_classification.keys()
        assert "sentiment" in expected_classification.keys()
        assert response.status_code == 200


class TestQuantifyUser:
    def test_non_existent_user(self, version, client, sentiment_setup_db):

        assert sentiment_setup_db

        response = client.post(f"api/{version}/sentiment/quantify/user/nonexistent")
        expected_prevalence = dict(response.json())

        assert expected_prevalence == {}
        assert response.status_code == 404

    def test_user_only(self, version, client, sentiment_setup_db):

        assert sentiment_setup_db

        user_id = utils.generate_md5("johndoe")

        response = client.post(f"api/{version}/sentiment/quantify/user/{user_id}")
        expected_prevalence = dict(response.json())

        assert expected_prevalence["negative"] == 1
        assert expected_prevalence["neutral"] == 1
        assert expected_prevalence["positive"] == 1
        assert response.status_code == 200

    def test_date_filter_only_date_from(self, version, client, sentiment_setup_db):

        assert sentiment_setup_db

        user_id = utils.generate_md5("johndoe")

        response = client.post(
            f"api/{version}/sentiment/quantify/user/{user_id}?date_from=2022-05-02"
        )
        expected_prevalence = dict(response.json())

        assert expected_prevalence["negative"] == 1
        assert expected_prevalence["neutral"] == 1
        assert response.status_code == 200

    def test_date_filter_only_date_to(self, version, client, sentiment_setup_db):

        assert sentiment_setup_db

        user_id = utils.generate_md5("johndoe")

        response = client.post(
            f"api/{version}/sentiment/quantify/user/{user_id}?date_to=2022-05-02"
        )
        expected_prevalence = dict(response.json())

        assert expected_prevalence["positive"] == 1
        assert expected_prevalence["negative"] == 1
        assert response.status_code == 200

    def test_date_filter_both(self, version, client, sentiment_setup_db):

        assert sentiment_setup_db

        user_id = utils.generate_md5("johndoe")

        response = client.post(
            f"api/{version}/sentiment/quantify/user/{user_id}?date_from=2022-05-02&date_to=2022-05-03"
        )
        expected_prevalence = dict(response.json())

        assert expected_prevalence["negative"] == 1
        assert expected_prevalence["neutral"] == 1
        assert response.status_code == 200


class TestClassifyHashtag:
    def test_non_existent_hashtag(self, version, client, sentiment_setup_db):

        assert sentiment_setup_db

        response = client.post(f"api/{version}/sentiment/quantify/hashtag/friday")
        expected_prevalence = dict(response.json())

        assert "negative" in expected_prevalence.keys()
        assert expected_prevalence["negative"] == 0

        assert "neutral" in expected_prevalence.keys()
        assert expected_prevalence["neutral"] == 0

        assert "positive" in expected_prevalence.keys()
        assert expected_prevalence["positive"] == 0

        assert response.status_code == 200

    def test_hashtag_only(self, version, client, sentiment_setup_db):

        assert sentiment_setup_db

        response = client.post(f"api/{version}/sentiment/quantify/hashtag/api")
        expected_prevalence = dict(response.json())

        assert expected_prevalence["negative"] == 1
        assert expected_prevalence["neutral"] == 1
        assert expected_prevalence["positive"] == 1
        assert response.status_code == 200

    def test_date_filter_date_from_only(self, version, client, sentiment_setup_db):

        assert sentiment_setup_db

        response = client.post(
            f"api/{version}/sentiment/quantify/hashtag/api?date_from=2022-05-02"
        )
        expected_prevalence = dict(response.json())

        assert expected_prevalence["negative"] == 1
        assert expected_prevalence["neutral"] == 1
        assert response.status_code == 200

    def test_date_filter_date_to_only(self, version, client, sentiment_setup_db):

        assert sentiment_setup_db

        response = client.post(
            f"api/{version}/sentiment/quantify/hashtag/api?date_to=2022-05-02"
        )
        expected_prevalence = dict(response.json())

        assert expected_prevalence["positive"] == 1
        assert expected_prevalence["negative"] == 1
        assert response.status_code == 200

    def test_date_filter_both(self, version, client, sentiment_setup_db):

        assert sentiment_setup_db

        response = client.post(
            f"api/{version}/sentiment/quantify/hashtag/api?date_from=2022-05-02&date_to=2022-05-03"
        )
        expected_prevalence = dict(response.json())

        assert expected_prevalence["negative"] == 1
        assert expected_prevalence["neutral"] == 1
        assert response.status_code == 200
