import json

from core import utils

import db

USERS_INDEX = utils.get_config("elasticsearch.indices", "users")
TWEETS_INDEX = utils.get_config("elasticsearch.indices", "tweets")


def initialize_indices():

    # delete indices if they already exists
    if db.es.indices.exists(USERS_INDEX):
        db.es.indices.delete(USERS_INDEX)

    if db.es.indices.exists(TWEETS_INDEX):
        db.es.indices.delete(TWEETS_INDEX)

    # load their mapping and create them
    with open("db/mappings/users.json") as f:
        db.es.indices.create(index=USERS_INDEX, body=json.load(f))

    with open("db/mappings/tweets.json") as f:
        db.es.indices.create(index=TWEETS_INDEX, body=json.load(f))


def populate_indices():

    # create "johndoe" user
    johndoe_document = {
        "id": utils.generate_md5("johndoe"),
        "username": "johndoe",
        "joined_at": "2022-05-01 09:30:00 -0300",
        "follows": [
            {
                "id": utils.generate_md5("terry"),
                "followed_at": "2022-05-01 12:00:00 -0300",
            }
        ],
        "followers": [],
    }

    db.es.create(index=USERS_INDEX, id=johndoe_document["id"], body=johndoe_document)

    # create "terry" user
    terry_document = {
        "id": utils.generate_md5("terry"),
        "username": "terry",
        "joined_at": "2022-05-01 09:30:00 -0300",
        "follows": [
            {
                "id": utils.generate_md5("caioueno"),
                "followed_at": "2022-05-05 17:00:00 -0300",
            }
        ],
        "followers": [
            {
                "id": utils.generate_md5("johndoe"),
                "followed_at": "2022-05-01 12:00:00 -0300",
            },
            {
                "id": utils.generate_md5("caioueno"),
                "followed_at": "2022-05-05 18:45:00 -0300",
            },
        ],
    }

    db.es.create(index=USERS_INDEX, id=terry_document["id"], body=terry_document)

    # create "caioueno" user
    caioueno_document = {
        "id": utils.generate_md5("caioueno"),
        "username": "caioueno",
        "joined_at": "2022-05-01 09:30:00 -0300",
        "follows": [
            {
                "id": utils.generate_md5("terry"),
                "followed_at": "2022-05-05 18:45:00 -0300",
            }
        ],
        "followers": [
            {
                "id": utils.generate_md5("terry"),
                "followed_at": "2022-05-05 17:00:00 -0300",
            }
        ],
    }

    db.es.create(index=USERS_INDEX, id=caioueno_document["id"], body=caioueno_document)

    # create tweets and retweets
    tweet_1 = {
        "id": utils.generate_md5("First tweet! #sideproject #fastapi" + "caioueno"),
        "author_id": utils.generate_md5("caioueno"),
        "tweeted_at": "2022-05-02 12:45:00 -0300",
        "text": "First tweet! #sideproject #fastapi",
        "sentiment": 1,
        "hashtags": ["#sideproject", "#fastapi"],
        "retweets": [],
        "likes": [
            {"id": utils.generate_md5("terry"), "liked_at": "2022-05-05 22:15:00 -0300"}
        ],
    }

    db.es.create(
        index=TWEETS_INDEX,
        id=tweet_1["id"],
        body=tweet_1,
    )

    tweet_2 = {
        "id": utils.generate_md5(
            "Awful to manually create those tweets >:c #setup #fastapi" + "caioueno"
        ),
        "author_id": utils.generate_md5("caioueno"),
        "tweeted_at": "2022-05-10 20:55:00 -0300",
        "text": "Awful to manually create those tweets >:c #setup #fastapi",
        "sentiment": -1,
        "hashtags": ["#setup", "#fastapi"],
        "retweets": [],
        "likes": [],
    }

    db.es.create(
        index=TWEETS_INDEX,
        id=tweet_2["id"],
        body=tweet_2,
    )

    tweet_3 = {
        "id": utils.generate_md5("Yeah! Almost there! #fastapi" + "terry"),
        "author_id": utils.generate_md5("terry"),
        "tweeted_at": "2022-05-07 03:10:00 -0300",
        "text": "Yeah! Almost there! #fastapi",
        "sentiment": -1,
        "hashtags": ["#fastapi"],
        "retweets": [
            {
                "id": utils.generate_md5("johndoe"),
                "retweeted_at": "2022-05-07 03:25:00 -0300",
            }
        ],
        "likes": [],
    }

    db.es.create(
        index=TWEETS_INDEX,
        id=tweet_3["id"],
        body=tweet_3,
    )


def main():

    initialize_indices()
    populate_indices()


if __name__ == "__main__":
    main()
