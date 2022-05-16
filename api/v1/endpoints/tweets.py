import logging
from typing import Any, List, Union

import db
from core import utils
from core.schemas import tweet, user
from fastapi import APIRouter, Response

USERS_INDEX = "users-index"
TWEETS_INDEX = "tweets-index"

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/{tweet_id}",
    response_model=Union[tweet.Tweet, tweet.ReferenceTweet, tweet.NotFoundTweet],
    status_code=200,
)
def get_tweet(tweet_id: str, response: Response) -> Any:

    if db.es.exists(index=TWEETS_INDEX, id=tweet_id):
        document = db.es.get(index=TWEETS_INDEX, id=tweet_id)["_source"]
    else:
        logger.warning(f"Document not found: {tweet_id}")
        document = {}
        response.status_code = 404

    return document


@router.get(
    "/user/{user_id}",
    response_model=List[tweet.Tweet],
    status_code=200,
)
def get_user_tweets(user_id: str, response: Response) -> Any:

    print(
        db.es.search(
            body={
                "query": {
                    "bool": {
                        "filter": {"term": {"author_id": utils.generate_md5("johndoe")}}
                    }
                }
            },
            index="tweets-index",
        )
    )
    return NotImplementedError()


@router.get(
    "/{user_id}/timeline",
    response_model=List[tweet.Tweet],
    status_code=200,
)
def get_user_timeline(user_id: str) -> Any:
    return NotImplementedError()


@router.post(
    "/{user_id}/tweet",
    response_model=Union[tweet.Tweet, tweet.EmptyTweet],
    status_code=201,
)
def publish_tweet(user_id: str, new_tweet: tweet.NewTweet, response: Response) -> Any:

    if not db.es.exists(index=USERS_INDEX, id=user_id):
        logger.warning(f"User not found: {user_id}")
        response.status_code = 404
        return {}

    document = db.es.get(index=USERS_INDEX, id=user_id)["_source"]
    logger.info(document)
    if db.es.exists(
        index=TWEETS_INDEX, id=utils.generate_md5(new_tweet.text + document["username"])
    ):
        logger.warning(f"User already tweeted the same text.")
        response.status_code = 409
        return db.es.get(
            index=TWEETS_INDEX,
            id=utils.generate_md5(new_tweet.text + document["username"]),
        )["_source"]

    # create new document otherwise
    new_document = {
        "id": utils.generate_md5(new_tweet.text + document["username"]),
        "author_id": document["id"],
        "tweeted_at": utils.time_now(),
        "text": new_tweet.text,
        "sentiment": 0,
        "hashtags": ["#api"],
        "retweets": [],
        "likes": [],
    }
    db.es.create(
        index=USERS_INDEX,
        id=utils.generate_md5(new_tweet.text + document["username"]),
        body=new_document,
    )

    return new_document


@router.post(
    "/{user_id}/retweet/{tweet_id}",
    response_model=Union[tweet.ReferenceTweet, tweet.EmptyReferenceTweet],
    status_code=201,
)
def retweet(user_id: str, tweet_id: str, response: Response) -> Any:

    if not db.es.exists(index=USERS_INDEX, id=user_id):
        response.status_code = 404
        return {}

    if not db.es.exists(index=TWEETS_INDEX, id=tweet_id):
        response.status_code = 404
        return {}

    tweet_doc = db.es.get(index=TWEETS_INDEX, id=tweet_id)["_source"]
    if user_id == tweet_doc["author_id"]:
        response.status_code = 500
        return {}

    db.es.update(
        index=TWEETS_INDEX,
        id=tweet_id,
        body={
            "script": {
                "source": """
                                if (!ctx._source.retweets.contains(ctx._source.retweets.find(f -> f.id == params.user.id))) {
                                        ctx._source.retweets.add(params.user)
                                    }
                          """,
                "lang": "painless",
                "params": {"user": {"id": user_id, "retweeted_at": utils.time_now()}},
            }
        },
    )

    # create new document otherwise
    new_document = {
        "id": utils.generate_md5(tweet_doc["id"] + user_id),
        "user_id": user_id,
        "referenced_at": utils.time_now(),
        "tweet_id": tweet_doc["id"],
    }

    db.es.create(
        index=USERS_INDEX,
        id=utils.generate_md5(tweet_doc["id"] + user_id),
        body=new_document,
    )

    return new_document


@router.post(
    "/{user_id}/like/{tweet_id}",
    response_model=Union[tweet.Tweet, tweet.EmptyTweet],
    status_code=201,
)
def like(user_id: str, tweet_id: str, response: Response) -> Any:

    if not db.es.exists(index=USERS_INDEX, id=user_id):
        response.status_code = 404
        return {}

    if not db.es.exists(index=TWEETS_INDEX, id=tweet_id):
        response.status_code = 404
        return {}

    document = db.es.get(index=TWEETS_INDEX, id=tweet_id)["_source"]
    if not document.get("author_id", False):
        response.status_code = 500
        return {}

    db.es.update(
        index=TWEETS_INDEX,
        id=tweet_id,
        body={
            "script": {
                "source": """
                                if (!ctx._source.likes.contains(ctx._source.likes.find(f -> f.id == params.user.id))) {
                                        ctx._source.likes.add(params.user)
                                    }
                          """,
                "lang": "painless",
                "params": {"user": {"id": user_id, "liked_at": utils.time_now()}},
            }
        },
    )

    return db.es.get(index=TWEETS_INDEX, id=tweet_id)["_source"]


@router.delete(
    "/{tweet_id}",
    response_model=Union[tweet.Tweet, tweet.ReferenceTweet, tweet.NotFoundTweet],
    status_code=200,
)
def delete_tweet(tweet_id: str, response: Response) -> Any:
    
    if not db.es.exists(index=TWEETS_INDEX, id=tweet_id):
        response.status_code = 404
        return {}

    document = db.es.get(index=TWEETS_INDEX, id=tweet_id)["_source"]

    if document.get("author_id", False):
        
        db.es.update_by_query()

        db.es.update(
            index=TWEETS_INDEX,
            id=tweet_id,
            body={"doc": {"retweets": [], "likes": []}},
        )

    # retrieve the updated document
    document = db.es.get(index=TWEETS_INDEX, id=tweet_id)["_source"]

    # permanently delete it
    db.es.delete(index=TWEETS_INDEX, id=tweet_id)

    return document