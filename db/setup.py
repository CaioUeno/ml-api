from core import utils

from db.client import es


def init_indices() -> bool:

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
    tweets_configs = {
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "author_id": {"type": "keyword"},
                "tweeted_at": {"type": "date", "format": "yyyy-MM-dd HH:mm:ss x"},
                "text": {"type": "text"},
                "sentiment": {"type": "integer"},
                "hashtags": {"type": "keyword"},
                "retweets": {
                    "type": "nested",
                    "properties": {
                        "id": {"type": "keyword"},
                        "retweeted_at": {
                            "type": "date",
                            "format": "yyyy-MM-dd HH:mm:ss x",
                        },
                    },
                },
                "likes": {
                    "type": "nested",
                    "properties": {
                        "id": {"type": "keyword"},
                        "liked_at": {"type": "date", "format": "yyyy-MM-dd HH:mm:ss x"},
                    },
                },
                "user_id": {"type": "keyword"},
                "referenced_at": {"type": "date", "format": "yyyy-MM-dd HH:mm:ss x"},
                "tweet_id": {"type": "keyword"},
            }
        }
    }

    es.indices.create(index="users-index", body=users_configs)
    es.indices.create(index="tweets-index", body=tweets_configs)


def close_indices():

    es.indices.delete("users-index")
    es.indices.delete("tweets-index")


def populate_indices():

    # test users
    testuser1 = "testuser1"
    es.create(
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
    es.create(
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
    es.create(
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
    es.create(
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

    # test tweet
    tweet1 = "opa opa"

    # remove time from id generation to make testing easier
    es.create(
        "tweets-index",
        id=utils.generate_md5(tweet1 + testuser1),
        body={
            "id": utils.generate_md5(tweet1 + testuser1),
            "author_id": utils.generate_md5(testuser1),
            "tweeted_at": utils.time_now(),
            "text": tweet1,
            "sentiment": 0,
            "hashtags": [],
            "retweets": [],
            "likes": [],
        },
    )


close_indices()
init_indices()
populate_indices()
